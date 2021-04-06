import re
import socket
import subprocess
import uuid
from typing import Optional
from typing import Union

import RPi.GPIO as GPIO
from numpy import exp


# set GPIOs at import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)


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


def update_led(
        red: Optional[bool] = None,
        yellow: Optional[bool] = None,
        green: Optional[bool] = None,
) -> None:
    if red is True:
        GPIO.output(23, GPIO.HIGH)
    else:
        GPIO.output(23, GPIO.LOW)

    if yellow is True:
        GPIO.output(24, GPIO.HIGH)
    else:
        GPIO.output(24, GPIO.LOW)

    if green is True:
        GPIO.output(25, GPIO.HIGH)
    else:
        GPIO.output(25, GPIO.LOW)
