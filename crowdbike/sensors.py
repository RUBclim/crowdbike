import logging
import threading
import time
from typing import Optional
from typing import Union

import adafruit_dht
import adafruit_gps
import board
import serial
from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_driver.linux_i2c_transceiver import LinuxI2cTransceiver
from sensirion_i2c_sht.sht3x import Sht3xI2cDevice

from crowdbike.helpers import update_led


class PmSensor(threading.Thread):
    def __init__(
            self,
            dev: str,
            logger: logging.Logger,
            baudrate: int = 9600,
    ) -> None:
        threading.Thread.__init__(self)
        self.running = False
        self.ser = serial.Serial(
            baudrate=baudrate,
            timeout=5,
            write_timeout=5,
        )
        # initialize later so no connection is established at initialization
        self.ser.port = dev
        self.pm2_5 = float('nan')
        self.pm10 = float('nan')
        self.logger = logger

    def run(self) -> None:
        while self.running:
            try:
                if not self.ser.isOpen():
                    self.ser.open()

                data = self.ser.read(10)
                assert data[0] == ord(b'\xaa')
                assert data[1] == ord(b'\xc0')
                assert data[9] == ord(b'\xab')
                checksum = sum(v for v in data[2:8]) % 256
                assert checksum == data[8]

                self.pm2_5 = (data[3] * 256 + data[2]) / 10.0
                self.pm10 = (data[5] * 256 + data[4]) / 10.0
                self.ser.close()
                update_led(yellow=True)
            except Exception as e:
                self.logger.warning(f'failed reading PM-sensor: {e}')
                self.pm10 = float('nan')
                self.pm2_5 = float('nan')
            finally:
                time.sleep(.1)
                update_led(yellow=False)
                time.sleep(.1)

    def sensor_sleep(self) -> None:
        '''
        set sensor to sleep mode
        originally from
        https://github.com/luetzel/sds011/blob/master/sds011_pylab.py
        '''
        if not self.ser.isOpen():
            self.ser.open()

        sleep_bytes = [
            b'\xaa', b'\xb4', b'\x06', b'\x01', b'\x00', b'\x00', b'\x00',
            b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00',
            b'\x00', b'\xff', b'\xff', b'\x05', b'\xab',
        ]
        for b in sleep_bytes:
            self.ser.write(b)

        self.ser.close()
        self.logger.info('set PM sensor to sleep mode')

    def sensor_wake(self) -> None:
        '''
        set sensor to awake mode
        originally from
        https://github.com/luetzel/sds011/blob/master/sds011_pylab.py
        '''
        if not self.ser.isOpen():
            self.ser.open()
        wake_bytes = [
            b'\xaa', b'\xb4', b'\x06', b'\x01', b'\x01', b'\x00', b'\x00',
            b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00',
            b'\x00', b'\xff', b'\xff', b'\x06', b'\xab',
        ]
        for b in wake_bytes:
            self.ser.write(b)

        self.ser.close()
        self.logger.info('set PM sensor to awake mode')


class DHT22(threading.Thread):
    def __init__(self, logger: logging.Logger) -> None:
        threading.Thread.__init__(self)
        self.dht_22 = adafruit_dht.DHT22(board.D4)
        self.running = True
        self.humidity: Optional[float] = None
        self.temperature: Optional[float] = None
        self.logger = logger

    def run(self) -> None:
        while self.running:
            try:
                self.humidity = self.dht_22.temperature
                self.temperature = self.dht_22.humidity
                # XXX: The DHT library kinda sucks, if the sensor throws
                # errors, because it was disconnected, self._temperature
                # stays at the old value so measurements remain the same
                # this way the LED is kinda useless!
                if self.temperature is not None:
                    update_led(red=True)
            except Exception as e:
                self.logger.warning(f'failed reading DHT22-sensor: {e}')
                continue
            finally:
                time.sleep(.1)
                update_led(red=False)
                time.sleep(.1)


class SHT85(threading.Thread):
    def __init__(self, logger: logging.Logger) -> None:
        threading.Thread.__init__(self)
        con = I2cConnection(LinuxI2cTransceiver('/dev/i2c-1'))
        self.sht_85 = Sht3xI2cDevice(con)
        self.running = True
        self.humidity = None
        self.temperature = None
        self.logger = logger

    def run(self) -> None:
        while self.running:
            try:
                temp, hum = self.sht_85.single_shot_measurement()
                self.temperature = temp.degrees_celsius
                self.humidity = hum.percent_rh
                update_led(red=True)
            except Exception as e:
                self.logger.warning(f'failed reading SHT85-sensor: {e}')
                continue
            finally:
                time.sleep(.1)
                update_led(red=False)
                time.sleep(.1)


class GPS(threading.Thread):
    '''Class for reading the adafruit gps'''

    def __init__(self, logger: logging.Logger) -> None:
        threading.Thread.__init__(self)
        self.uart = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.gps.send_command(b'PMTK220,1000')
        self.running = True

        self.has_fix: Optional[bool] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.satellites: Union[int, float] = float('nan')
        self.timestamp: str = 'nan'
        self.alt: Optional[float] = None
        self.speed: Union[int, float] = float('nan')
        self.logger = logger

    def run(self) -> None:
        '''start thread and get values'''
        while self.running:
            try:
                self.gps.update()
                self.has_fix = self.gps.has_fix
                if self.gps.satellites is not None:
                    self.satellites = self.gps.satellites
                else:
                    self.satellites = float('nan')

                if self.gps.latitude is not None:
                    self.latitude = self.gps.latitude
                else:
                    self.latitude = float('nan')

                if self.gps.longitude is not None:
                    self.longitude = self.gps.longitude
                else:
                    self.longitude = float('nan')

                if self.gps.altitude_m is not None:
                    self.alt = self.gps.altitude_m
                else:
                    self.alt = float('nan')

                if self.gps.speed_knots is not None:
                    self.speed = self.gps.speed_knots
                else:
                    self.speed = float('nan')

                if self.gps.timestamp_utc is not None:
                    self.timestamp = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        self.gps.timestamp_utc,
                    )
                if self.has_fix is True:
                    update_led(green=True)
            except Exception as e:
                self.logger.warning(f'failed reading GPS: {e}')
                continue
            finally:
                time.sleep(.1)
                update_led(green=False)
                time.sleep(.1)

    def stop(self) -> None:
        '''close uart port when terminating'''
        self.uart.close()
        self.logger.info('closed GPS UART port')

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'uart={self.uart!r}, '
            f'gps={self.gps!r}, '
            f'running={self.running!r}, '
            f'has_fix={self.has_fix!r}, '
            f'latitude={self.latitude!r}, '
            f'longitude={self.longitude!r}, '
            f'satellites={self.satellites!r}, '
            f'timestamp={self.timestamp!r}, '
            f'alt={self.alt!r}, '
            f'speed={self.speed!r}, '
            f'logger={self.logger!r}'
            ')'
        )
