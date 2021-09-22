import logging
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import uuid
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import RPi.GPIO as GPIO
from tkinter import Label
from tkinter import messagebox
from tkinter import Tk
from tkinter import ttk

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
        0.6113 * math.exp(
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
    theme = importlib_resources.read_text('crowdbike.resources', 'theme.json')
    with open(os.path.join(CONFIG_DIR, 'config.json'), 'w') as f:
        f.write(cfg)

    with open(os.path.join(CONFIG_DIR, 'calibration.json'), 'w') as f:
        f.write(calib)

    with open(os.path.join(CONFIG_DIR, 'theme.json'), 'w') as f:
        f.write(theme)


def create_logger(
        logdir: str,
        loglevel: str = 'WARNING',
) -> logging.Logger:
    LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if loglevel not in LEVELS:
        raise ValueError(f'loglevel must be one of {", ".join(LEVELS)}')

    dirname = os.path.dirname(logdir)
    if dirname != '':
        os.makedirs(dirname, exist_ok=True)

    logger = logging.getLogger('crowdbike')
    file_handler = logging.FileHandler(logdir)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(loglevel)
    return logger


def upload_to_cloud(
        verbose: bool,
        config: Dict[str, Any],
        logger: logging.Logger,
        *,
        root: Optional[Tk] = None,
        theme: Optional[Dict[str, str]] = None,
) -> None:
    if root is not None and theme is not None:
        pb = ttk.Progressbar(
            root,
            orient='horizontal',
            mode='determinate',
            length=500,
        )
        pb.grid(row=16, column=0, columnspan=3)
        progress_txt = Label(
            root, text='',
            bg=theme['bg_col'],
            fg=theme['fg_col'],
            font=(theme['f_family'], 14),
        )
        progress_txt.grid(row=17, columnspan=3,  pady=(0, 10))
        pb.start()

    try:
        log_dir = config['user']['logfile_path']
        archive_dir = os.path.join(log_dir, 'archive')
        folder_token = config['cloud']['folder_token']
        passwd = config['cloud']['passwd']
        base_url = config['cloud']['base_url']
        # we need a trailing slash for the url to be valid
        if not base_url[-1] == '/':
            base_url += '/'

        os.makedirs(archive_dir, exist_ok=True)

        files_present = False
        for element in os.listdir(log_dir):
            if os.path.isfile(os.path.join(log_dir, element)):
                files_present = True
                break

        if verbose:
            first_args = '-vT'
        else:
            first_args = '-T'

        if files_present:
            files = os.listdir(log_dir)
            nr_files = len(files)
            for idx, log in enumerate(files):
                if os.path.splitext(log)[1].lower() == '.csv':
                    status = f'uploading: {log} to the cloud'
                    if root is not None:
                        progress_txt.config(text=status)
                        pb['value'] = ((idx + 1) * 100) / nr_files
                        root.update_idletasks()

                    logger.info(status)
                    print(status)
                    curl_call = [
                        'curl', first_args, os.path.join(log_dir, log), '-u',
                        f'{folder_token}:{passwd}', '-H',
                        'X-Requested-With:XMLHttpRequest',
                        f'{base_url}public.php/webdav/{log}',
                    ]
                    logger.debug(f'curl call sent: {curl_call}')
                    if verbose:
                        c = subprocess.run(args=curl_call, capture_output=True)
                        stdoutput = c.stdout.decode('utf-8')
                        stderr = c.stderr.decode('utf-8')
                        logging.debug(stderr)
                        print(stderr)
                        err = stderr.split('curl:')

                        if stdoutput == '' and len(err) == 1:
                            shutil.move(os.path.join(log_dir, log), archive_dir)  # noqa E501
                        else:
                            logger.debug(' error '.center(79, '='))
                            print(' error '.center(79, '='))
                            logger.debug(stdoutput)
                            print(stdoutput)
                            logger.debug(err)
                            print(err)

                    else:
                        c = subprocess.run(args=curl_call, capture_output=True)
                        stdoutput = c.stdout.decode('utf-8')
                        stderr = c.stderr.decode('utf-8')
                        err = stderr.split('curl:')

                        if stdoutput == '' and len(err) == 1:
                            shutil.move(
                                os.path.join(
                                    log_dir, log,
                                ), archive_dir,
                            )
                        else:
                            logger.debug(' error '.center(79, '='))
                            print(' error '.center(79, '='))
                            logger.debug(stdoutput)
                            print(stdoutput)
                            logger.debug(err)
                            print(err)
            if root is not None:
                progress_txt.config(text='')
                pb.stop()
                pb.grid_forget()
                messagebox.showinfo(
                    title='upload successfull',
                    message=f'successfully uploaded {nr_files} files',
                )
        elif not files_present:
            nothing_to_do = (
                f'Everything up to date. '
                f'There are no files to upload in "{log_dir}"'
            )
            if root is not None:
                pb.grid_forget()
                messagebox.showinfo(title='test', message=nothing_to_do)

            logger.info(nothing_to_do)
            print(nothing_to_do)
        else:
            raise Exception(
                f'An unknown error occurred. {files_present} is not a boolean',
            )
    except Exception as e:
        err_msg = f'An error occurred while uploading:\n{e}'
        if root is not None:
            pb.grid_forget()
            messagebox.showerror(
                title='Error',
                message=err_msg,
            )
        else:
            logger.error(err_msg)
            print(err_msg)
    finally:
        if root is not None:
            pb.stop()
            pb.grid_forget()
            progress_txt.grid_forget()
        else:
            pass
