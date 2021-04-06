import os
import re
import socket
import subprocess
import sys
import uuid
from typing import Optional
from typing import Union

import RPi.GPIO as GPIO
from numpy import exp

if sys.version_info < (3, 8):  # pragma: no cover (>=py38)
    import importlib_resources
else:  # pragma: no cover (<py38)
    import importlib.resources as importlib_resources


CONFIG_DIR = os.path.expanduser('~/.config/crowdbike')


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


def setup_config() -> None:
    if os.path.exists(CONFIG_DIR):
        choice = input(
            'the config directory already exists, '
            'if you continue, it will be overwritten (yes/no): ',
        )
        if choice == 'yes' or choice == 'y':
            _make_config_dirs()
        else:
            return
    else:
        _make_config_dirs()


def _make_config_dirs() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    cfg = importlib_resources.read_text('crowdbike.resources', 'config.json')
    calib = importlib_resources.read_text(
        'crowdbike.resources',
        'calibration.json',
    )
    with open(os.path.join(CONFIG_DIR, 'config.json'), 'w') as f:
        f.write(cfg)

    with open(os.path.join(CONFIG_DIR, 'calibration.json'), 'w') as f:
        f.write(calib)
