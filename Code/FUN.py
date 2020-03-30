import socket

import adafruit_dht
import serial
from numpy import nan
from retry import retry


def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class pm_sensor:
    def __init__(self, dev: str, baudrate: int = 9600) -> None:
        self.dev = dev
        self.baudrate = baudrate
        # initialize serial port
        global ser
        ser = serial.Serial()
        ser.port = self.dev
        ser.baudrate = self.baudrate

    def read_pm(self) -> None:
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
            return(measures)
        except:
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


@retry(tries=5)
def read_dht22(sensor: adafruit_dht.DHT22)  -> dict:
    temp = sensor.temperature
    hum = sensor.humidity
    if temp is None:
        temp = nan
    if hum is None:
        hum = nan
    return {'temperature': temp, 'humidity': hum}
