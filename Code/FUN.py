import re
import socket
import subprocess
import threading
import time
import uuid
from typing import Dict
from typing import Optional
from typing import Union

import adafruit_dht
import adafruit_gps
import serial
from numpy import exp
from numpy import nan


def get_wlan_macaddr() -> str:
    ifconfig = subprocess.check_output(args=('ifconfig', '-a')).decode('utf-8')
    match = re.search(r'(?:ether\s)([0-9a-f:]+)', ifconfig)
    if match is not None:
        mac_address = match.groups()[0]
    else:
        mac_address = str(uuid.getnode())
    return mac_address


def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class PmSensor:
    def __init__(self, dev: str, baudrate: int = 9600) -> None:
        self.dev = dev
        self.baudrate = baudrate
        # initialize serial port
        global ser
        ser = serial.Serial()
        ser.port = self.dev
        ser.baudrate = self.baudrate

    def read_pm(self) -> Dict[str, Union[float, nan]]:
        '''
        method for reading the Nova-PM-sensor
        dev must be type <str> e.g. '/dev/ttyUSB0'
        originally from
        https://gist.github.com/marw/9bdd78b430c8ece8662ec403e04c75fe
        '''

        try:
            # open connection
            if not ser.isOpen():
                ser.open()

            # read data
            bytes = ser.read(10)
            assert bytes[0] == ord(b'\xaa')
            assert bytes[1] == ord(b'\xc0')
            assert bytes[9] == ord(b'\xab')

            pm2_5 = (bytes[3] * 256 + bytes[2]) / 10.0
            pm10 = (bytes[5] * 256 + bytes[4]) / 10.0

            checksum = sum(v for v in bytes[2:8]) % 256
            assert checksum == bytes[8]

            measures = {'PM10': pm10, 'PM2_5': pm2_5}

            ser.close()
        except Exception:
            measures = {'PM10': nan, 'PM2_5': nan}

        return measures

    def sensor_sleep(self) -> None:
        '''
        set sensor to sleep mode
        originally from
        https://github.com/luetzel/sds011/blob/master/sds011_pylab.py
        '''
        if not ser.isOpen():
            ser.open()

        bytes = [
            b'\xaa',  # head
            b'\xb4',  # command 1
            b'\x06',  # data byte 1
            b'\x01',  # data byte 2 (set mode)
            b'\x00',  # data byte 3 (sleep)
            b'\x00',  # data byte 4
            b'\x00',  # data byte 5
            b'\x00',  # data byte 6
            b'\x00',  # data byte 7
            b'\x00',  # data byte 8
            b'\x00',  # data byte 9
            b'\x00',  # data byte 10
            b'\x00',  # data byte 11
            b'\x00',  # data byte 12
            b'\x00',  # data byte 13
            b'\xff',  # data byte 14 (device id byte 1)
            b'\xff',  # data byte 15 (device id byte 2)
            b'\x05',  # checksum
            b'\xab',  # tail
        ]

        for b in bytes:
            ser.write(b)

        ser.close()

    def sensor_wake(self) -> None:
        '''
        set sensor to awake mode
        originally from
        https://github.com/luetzel/sds011/blob/master/sds011_pylab.py
        '''
        if not ser.isOpen():
            ser.open()
        bytes = [
            b'\xaa',  # head
            b'\xb4',  # command 1
            b'\x06',  # data byte 1
            b'\x01',  # data byte 2 (set mode)
            b'\x01',  # data byte 3 (sleep)
            b'\x00',  # data byte 4
            b'\x00',  # data byte 5
            b'\x00',  # data byte 6
            b'\x00',  # data byte 7
            b'\x00',  # data byte 8
            b'\x00',  # data byte 9
            b'\x00',  # data byte 10
            b'\x00',  # data byte 11
            b'\x00',  # data byte 12
            b'\x00',  # data byte 13
            b'\xff',  # data byte 14 (device id byte 1)
            b'\xff',  # data byte 15 (device id byte 2)
            b'\x06',  # checksum
            b'\xab',  # tail
        ]

        for b in bytes:
            ser.write(b)

        ser.close()


def read_dht22(sensor: adafruit_dht.DHT22) -> Dict[str, str]:
    temp = sensor.temperature
    hum = sensor.humidity
    if temp is None:
        temp = nan
    if hum is None:
        hum = nan
    return {'temperature': temp, 'humidity': hum}


def sat_vappressure(temp: Union[int, float]) -> float:
    saturation_vappress = (
        0.6113 * exp(
            (2501000.0 / 461.5) * ((1.0 / 273.15) - (1.0 / (temp + 273.15))),
        )
    )
    return saturation_vappress


def vappressure(
        humidity: Union[int, float],
        saturation_vappress: Union[int, float],
) -> float:
    vappress = ((humidity / 100.0) * saturation_vappress)
    return vappress


class TemperatureSensor(threading.Thread):
    def __init__(self, dht_22: adafruit_dht.DHT22) -> None:
        threading.Thread.__init__(self)
        self.dht_22 = dht_22
        self.running = True
        self.humidity = None
        self.temperature = None

    def run(self) -> None:
        while self.running:
            try:
                self.humidity = self.dht_22.temperature
                self.temperature = self.dht_22.humidity
            except Exception:
                continue
            time.sleep(.1)


class GPS(threading.Thread):
    '''Class for reading the adafruit gps'''

    def __init__(self) -> None:
        threading.Thread.__init__(self)
        self.uart = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.gps.send_command(b'PMTK220,1000')
        self.running = True

        self.has_fix: Optional[bool] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.satellites: Optional[int] = None
        self.timestamp: Optional[str] = None
        self.alt: Optional[float] = None
        self.speed: Optional[float] = None

    def run(self) -> None:
        '''start thread and get values'''
        while self.running:
            try:
                self.gps.update()
                self.has_fix = self.gps.has_fix
                if self.gps.satellites is not None:
                    self.satellites = self.gps.satellites
                else:
                    self.satellites = nan

                if self.gps.latitude is not None:
                    self.latitude = self.gps.latitude
                else:
                    self.latitude = nan

                if self.gps.longitude is not None:
                    self.longitude = self.gps.longitude
                else:
                    self.longitude = nan

                if self.gps.altitude_m is not None:
                    self.alt = self.gps.altitude_m
                else:
                    self.alt = nan

                if self.gps.speed_knots is not None:
                    self.speed = self.gps.speed_knots
                else:
                    self.speed = nan

                if self.gps.timestamp_utc is not None:
                    self.timestamp = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        self.gps.timestamp_utc,
                    )
                time.sleep(.1)
            except Exception:
                continue

    def stop(self) -> None:
        '''close uart port when terminating'''
        self.uart.close()
