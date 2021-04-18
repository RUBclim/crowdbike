"""
Program <crowdbike.py> to read and record GPS data,
air temperature and humidity
using Adafruit's Ultimate GPS and a
DHT22 temperature sensor while riding
on a bike.

First established at:
    University of Freiburg
    Environmental Meteology
    Version 1.2
    Written by Heinz Christen Mar 2018
    Modified by Andreas Christen Apr 2018
    https://github.com/achristen/Meteobike

Modified Apr 2020:
    Ruhr-University Bochum
    Urban Climatology Group
    Jonas Kittner
    added a nova PM-sensor to the kit
    made a non-GUI version to run in background
    reworked all internals - using adafruit blinka circuitpython library

Buttons:
    Record:  Start recording in append mode to logfile, but only if gps has fix
    PM-Sensor: Switch On/Off the pm sensor or deactivate it when
    no one is connected
    Stop:  Stop recording (Pause)
    Exit:  exit program
"""
import argparse
import json
import os
import sys
from datetime import datetime
from typing import NoReturn
from typing import Optional
from typing import Union

import RPi.GPIO as GPIO
from serial.serialutil import SerialException
from tkinter import Button
from tkinter import DISABLED
from tkinter import E
from tkinter import font
from tkinter import HORIZONTAL
from tkinter import Label
from tkinter import mainloop
from tkinter import NORMAL
from tkinter import Scale
from tkinter import Tk
from tkinter import W
from tkinter.ttk import Separator

from crowdbike.helpers import CONFIG_DIR
from crowdbike.helpers import create_logger
from crowdbike.helpers import get_ip
from crowdbike.helpers import get_wlan_macaddr
from crowdbike.helpers import sat_vappressure
from crowdbike.helpers import setup_config
from crowdbike.helpers import upload_to_cloud
from crowdbike.helpers import vappressure
from crowdbike.sensors import DHT22
from crowdbike.sensors import GPS
from crowdbike.sensors import PmSensor
from crowdbike.sensors import SHT85


if sys.version_info < (3, 8):  # pragma: no cover (>=py38)
    import importlib_metadata
else:  # pragma: no cover (<py38)
    import importlib.metadata as importlib_metadata


class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status: int = 0, message: Optional[str] = None) -> NoReturn:
        GPIO.cleanup()
        if message:
            self._print_message(message, sys.stderr)
        exit(status)


parser = ArgumentParser()
parser.add_argument('command', choices=['init', 'run', 'upload'])
parser.add_argument(
    '-V', '--version',
    action='version',
    version=f'%(prog)s {importlib_metadata.version("crowdbike")}',
)
parser.add_argument(
    '--logfile',
    type=str,
    default=os.path.expanduser('~/crowdbike.log'),
    help='file to write the logs to',
)
parser.add_argument(
    '--loglevel',
    type=str,
    default='WARNING',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
)
args = parser.parse_args()
if args.command == 'init':
    setup_config()
    GPIO.cleanup()
    exit(0)

logger = create_logger(logdir=args.logfile, loglevel=args.loglevel)
logger.info('started crowdbike...')
logger.info(f'arguments passed: {args}')

# __load config files__
with open(os.path.join(CONFIG_DIR, 'config.json')) as cfg:
    config = json.load(cfg)
    logger.info(f'configuration loaded: {json.dumps(config, indent=2)}')

if args.command == 'upload':
    if args.loglevel == 'DEBUG':
        verbose = True
    else:
        verbose = False

    upload_to_cloud(verbose=verbose, config=config, logger=logger)
    GPIO.cleanup()
    exit(0)

raspberryid = config['user']['bike_nr']
studentname = config['user']['studentname']
mac = get_wlan_macaddr()

with open(os.path.join(CONFIG_DIR, 'calibration.json')) as cal:
    calib = json.load(cal)
    logger.info(f'calibration loaded: {json.dumps(calib, indent=2)}')

# __calibration params__
temperature_cal_a1 = calib['temp_cal_a1']
temperature_cal_a0 = calib['temp_cal_a0']
hum_cal_a1 = calib['hum_cal_a1']
hum_cal_a0 = calib['hum_cal_a0']

window_title = f'Crowdbike {raspberryid}'
logfile_path = config['user']['logfile_path']
os.makedirs(logfile_path, exist_ok=True)

log_time = datetime.utcnow().strftime('%Y-%m-%d_%H%M%S')
logfile_name = f"{raspberryid}_{studentname.replace(' ', '_')}_{log_time}.csv"
logfile = os.path.join(logfile_path, logfile_name)
logger.info(f'writing measurement logs to {logfile}')

counter = 0

# initialize threads
gpsp = GPS(logger)
gpsp.start()

temp_hum_sensor: Union[DHT22, SHT85]
sensor_type = config['user']['sensor_type']
if sensor_type == 'SHT85':
    temp_hum_sensor = SHT85(logger)
    logger.info('using SHT85 sensor')
elif sensor_type == 'DHT22':
    temp_hum_sensor = DHT22(logger)
    logger.info('using DHT22 sensor')
else:
    raise NameError('sensor type unknown, must be either SHT85 or DHT22')

temp_hum_sensor.start()
nova_pm = PmSensor(dev='/dev/ttyUSB0', logger=logger)

# global variables
with open(os.path.join(CONFIG_DIR, 'theme.json')) as t:
    theme = json.load(t)
    logger.info(f'theme loaded: {json.dumps(theme, indent=2)}')

recording = False

pm_status = nova_pm.running = config['user']['pm_sensor']
# switch off sensor if it running prior to starting the app
if pm_status is False:
    try:
        nova_pm.sensor_sleep()
    except SerialException:
        logger.warning('could not set PM sensor to sleep mode (startup)')

sampling_rate = config['user']['sampling_rate']

cnames = [
    'id',
    'record',
    'raspberry_time',
    'gps_time',
    'altitude',
    'latitude',
    'longitude',
    'speed',
    'temperature',
    'temperature_raw',
    'rel_humidity',
    'rel_humidity_raw',
    'vapour_pressure',
    'pm10',
    'pm2_5',
    'mac',
]


# __functions__
def exit_program() -> None:
    logger.info('exiting programm...')
    master.destroy()
    gpsp.running = False
    gpsp.stop()
    gpsp.join()
    temp_hum_sensor.running = False
    temp_hum_sensor.join()
    nova_pm.running = False
    # only try joining the thread if it was running
    if nova_pm.isAlive():
        nova_pm.join()
    GPIO.cleanup()
    exit(0)


def record_data() -> None:
    global recording
    recording = True
    b_stop.config(state=NORMAL)
    b_record.config(state=DISABLED)
    b_upload.config(state=DISABLED)

    if os.path.isfile(logfile):
        return
    else:
        f0 = open(logfile, 'w')
        for i in range(0, len(cnames)-1):
            f0.write(f'{cnames[i]},')
        f0.write(f'{cnames[len(cnames)-1]}\n')
        f0.close()


def stop_data() -> None:
    global recording
    recording = False
    logger.info('recording stopped')
    b_record.config(state=NORMAL)
    b_stop.config(state=DISABLED)
    b_upload.config(state=NORMAL)


# tkinter button slider function
def set_pm_status(value: str) -> None:
    global pm_slider
    global pm_status
    global nova_pm
    if value == '1':
        pm_status = True
        pm_slider['troughcolor'] = '#20ff20'
        try:
            nova_pm.sensor_wake()
            # reinitialize thread so it gets a new PID
            nova_pm = PmSensor(dev='/dev/ttyUSB0', logger=logger)
            nova_pm.running = True
            nova_pm.start()
        except Exception as e:
            logger.warning(f'failed reading the PM sensor (main): {e}')
            pass
    else:
        pm_status = False
        pm_slider['troughcolor'] = '#c10000'
        try:
            nova_pm.running = False
            nova_pm.join()
            nova_pm.sensor_sleep()
        except Exception as e:
            logger.warning(f'failed setting the PM to sleep mode (main) {e}')
            pass


def start_counting(label: Label) -> None:
    counter = 0

    def count() -> None:
        global counter
        counter += 1
        computer_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # get sensor readings from DHT-sensor
        try:
            humidity = temp_hum_sensor.humidity or float('nan')
            temperature = temp_hum_sensor.temperature or float('nan')
        except Exception as e:
            logger.warning(f'reading the temp sensor failed (main): {e}')
            humidity = float('nan')
            temperature = float('nan')

        # calculate temperature with sensor calibration values
        temperature_raw = round(temperature, 5)
        temperature_calib = round(
            temperature * temperature_cal_a1 + temperature_cal_a0,
            3,
        )
        humidity_raw = round(humidity, 5)
        humidity_calib = round(
            humidity * hum_cal_a1 + hum_cal_a0,
            3,
        )

        saturation_vappress = sat_vappressure(temperature_calib)
        vappress = round(
            vappressure(
                humidity_calib,
                saturation_vappress,
            ), 5,
        )

        # read pm-sensor
        if pm_status is True:
            pm2_5 = nova_pm.pm2_5
            pm10 = nova_pm.pm10
        else:
            pm2_5 = float('nan')
            pm10 = float('nan')

        if humidity > 100:
            humidity = 100

        # Get GPS position
        gps_time = gpsp.timestamp
        gps_altitude = gpsp.alt
        gps_latitude = gpsp.latitude
        gps_longitude = gpsp.longitude
        gps_speed = round(gpsp.speed * 1.852, 2)
        f_mode = gpsp.satellites  # store number of satellites
        has_fix = False  # assume no fix

        if f_mode == 2:
            value_counter.config(bg='orange')
        elif f_mode > 2:
            has_fix = True
            value_counter.config(bg='#20ff20')
        else:
            value_counter.config(bg='red')

        # __format value display in gui__
        value_ctime.config(text=computer_time)
        value_altitude.config(text=f'{gps_altitude:.3f} m ASL')
        value_latitude.config(text=f'{gps_latitude:.6f} °N')
        value_longitude.config(text=f'{gps_longitude:.6f} °E')
        value_speed.config(text=f'{gps_speed:.1f} km/h')
        value_time.config(text=gps_time)
        value_temperature.config(
            text='{:.1f} °C'.format(
                temperature_calib,
            ),
        )
        value_humidity.config(text=f'{humidity_calib:.1f} %')
        value_vappress.config(text=f'{vappress:.3f} kPa')

        value_pm10.config(text=f'{pm10:.1f} \u03BCg/m\u00B3')
        value_pm2_5.config(text=f'{pm2_5:.1f} \u03BCg/m\u00B3')

        label.config(text=str(counter))
        label.after(1000 * sampling_rate, count)

        if recording and has_fix:
            with open(logfile, 'a') as f0:
                f0.write(raspberryid + ',')
                f0.write(str(counter) + ',')
                f0.write(computer_time + ',')
                if has_fix:
                    f0.write(gps_time + ',')
                else:
                    f0.write('nan,')

                f0.write(f'{gps_altitude:.3f}' + ',')
                f0.write(f'{gps_latitude:.6f}' + ',')
                f0.write(f'{gps_longitude:.6f}' + ',')
                f0.write(f'{gps_speed:.1f}' + ',')

                f0.write(str(temperature_calib) + ',')
                f0.write(str(temperature_raw) + ',')

                f0.write(str(humidity_calib) + ',')
                f0.write(str(humidity_raw) + ',')

                f0.write(str(vappress) + ',')

                f0.write(str(pm10) + ',')
                f0.write(str(pm2_5) + ',')
                f0.write(str(mac) + '\n')

    count()


# define widgets
master = Tk()
master.protocol('WM_DELETE_WINDOW', exit_program)
master.configure(background=theme['bg_col'])
default_font = font.nametofont('TkDefaultFont')
default_font.configure(size=theme['font_size'], family=theme['f_family'])
master.title(window_title)
# master.attributes('-fullscreen', True)
Label(
    master, text=' Name', fg=theme['fg_header'],
    bg=theme['bg_col'],
).grid(row=0, column=0, sticky=W)
Label(
    master, text=studentname + "'s Crowdbike", fg=theme['fg_header'],
    bg=theme['bg_col'],
).grid(row=0, column=1, sticky=W, columnspan=2)
Label(
    master, text=f'IP: {get_ip()}', fg=theme['fg_header'], bg=theme['bg_col'],
).grid(row=1, column=1, sticky=E, columnspan=2)
Label(
    master, text=' PM-Sensor', fg=theme['fg_header'],
    bg=theme['bg_col'],
).grid(row=1, column=0, sticky=W, columnspan=2)
Separator(master, orient=HORIZONTAL).grid(
    row=2, columnspan=3, sticky='ew', pady=(10, 10),
)
# define labels
label_counter = Label(
    master, text=' Counter',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_counter.grid(row=3, column=0, sticky=W)

label_ctime = Label(
    master, text=' Time',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_ctime.grid(row=4, column=0, sticky=W)

label_altitude = Label(
    master, text=' Altitude',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_altitude.grid(row=5, column=0, sticky=W)

label_latitude = Label(
    master, text=' Latitude',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_latitude.grid(row=6, column=0, sticky=W)

label_longitude = Label(
    master, text=' Longitude',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_longitude.grid(row=7, column=0, sticky=W)

label_speed = Label(
    master, text=' Speed',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_speed.grid(row=8, column=0, sticky=W)

label_time = Label(
    master, text=' GPS Time',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_time.grid(row=9, column=0, sticky=W)

label_temperature = Label(
    master, text=' Temperature',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_temperature.grid(row=10, column=0, sticky=W)

label_humidity = Label(
    master, text=' Rel. Humidity',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_humidity.grid(row=11, column=0, sticky=W)

label_vappress = Label(
    master, text=' Vap. Pressure   ',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_vappress.grid(row=12, column=0, sticky=W)

# labels for pm sensor
label_pm10 = Label(
    master, text=' PM 10 ',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_pm10.grid(row=13, column=0, sticky=W)

label_pm2_5 = Label(
    master, text=' PM 2.5 ',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
label_pm2_5.grid(row=14, column=0, sticky=W)

# define values (constructed also as labels, text will be modified in count)
value_counter = Label(master, text=' Counter', bg='red', fg=theme['fg_col'])
value_counter.grid(row=3, column=1, sticky=W, columnspan=2)

value_ctime = Label(
    master, text=' Time',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_ctime.grid(row=4, column=1, sticky=W, columnspan=2)

value_altitude = Label(
    master, text=' Altitude',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_altitude.grid(row=5, column=1, sticky=W, columnspan=2)

value_latitude = Label(
    master, text=' Latitude',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_latitude.grid(row=6, column=1, sticky=W, columnspan=2)

value_longitude = Label(
    master, text=' Longitude',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_longitude.grid(row=7, column=1, sticky=W, columnspan=2)

value_speed = Label(
    master, text=' Speed',
    bg=theme['bg_col'], fg=theme['fg_col'],
)

value_speed.grid(row=8, column=1, sticky=W, columnspan=2)

value_time = Label(
    master, text='GPS Time ---------------',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_time.grid(row=9, column=1, sticky=W, columnspan=2)

value_temperature = Label(
    master, text=' Temperature',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_temperature.grid(row=10, column=1, sticky=W, columnspan=2)

value_humidity = Label(
    master, text=' Rel. Humidity',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_humidity.grid(row=11, column=1, sticky=W, columnspan=2)

value_vappress = Label(
    master, text=' Vap. Pressure ',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_vappress.grid(row=12, column=1, sticky=W, columnspan=2)

value_pm10 = Label(
    master, text=' PM 10 ',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_pm10.grid(row=13, column=1, sticky=W, columnspan=2)
value_pm2_5 = Label(
    master, text=' PM 2.5 ',
    bg=theme['bg_col'], fg=theme['fg_col'],
)
value_pm2_5.grid(row=14, column=1, sticky=W, columnspan=2)

# initialize value_counter
start_counting(value_counter)
Separator(master, orient=HORIZONTAL).grid(
    row=15, columnspan=3, sticky='ew', pady=(10, 0),
)
# define buttons
b_record = Button(
    master,
    text='Record',
    width=7,
    state=DISABLED,
    bg=theme['b_col'],
    fg=theme['fg_col'],
    font=(theme['f_family'], 12, 'bold'),
    disabledforeground=theme['b_disabled'],
    command=record_data,
    activeforeground=theme['fg_col'],
    activebackground=theme['b_hover'],
    highlightcolor=theme['b_hl_border'],
    highlightbackground=theme['b_hl_border'],
    highlightthickness=1,

)
b_record.grid(row=16, column=0, sticky=W, padx=(20, 0), pady=(20, 20))

b_stop = Button(
    master,
    text='Stop',
    width=7,
    bg=theme['b_col'],
    fg=theme['fg_col'],
    font=(theme['f_family'], 12, 'bold'),
    state=DISABLED, command=stop_data,
    disabledforeground=theme['b_disabled'],
    activeforeground=theme['fg_col'],
    activebackground=theme['b_hover'],
    highlightcolor=theme['b_hl_border'],
    highlightbackground=theme['b_hl_border'],
    highlightthickness=1,
)
b_stop.grid(row=16, column=1, sticky=W, padx=(20, 40), pady=(20, 20))

b_exit = Button(
    master,
    text='Exit',
    width=7,
    bg=theme['b_col'],
    fg=theme['fg_col'],
    font=(theme['f_family'], 12, 'bold'),
    state=NORMAL, command=exit_program,
    activeforeground=theme['fg_col'],
    activebackground=theme['b_hover'],
    highlightcolor=theme['b_hl_border'],
    highlightbackground=theme['b_hl_border'],
    highlightthickness=1,
)
b_exit.grid(row=16, column=2, sticky=W, pady=(20, 20))

b_upload = Button(
    master,
    text='upload',
    width=7,
    state=DISABLED,
    command=lambda: upload_to_cloud(
        verbose=False, config=config, logger=logger,
    ),
    fg=theme['fg_col'],
    bg=theme['b_col'],
    font=(theme['f_family'], 12, 'bold'),
    disabledforeground=theme['b_disabled'],
    activeforeground=theme['fg_col'],
    activebackground=theme['b_hover'],
    highlightcolor=theme['b_hl_border'],
    highlightbackground=theme['b_hl_border'],
    highlightthickness=1,
)
b_upload.grid(row=16, column=0, sticky=E, padx=(0, 20), pady=(20, 20))

# slider
pm_slider = Scale(
    orient=HORIZONTAL, length=80, to=1, label='',
    showvalue=False, sliderlength=40, troughcolor='#666666',
    width=30, command=set_pm_status,
    fg=theme['fg_col'],
    bg=theme['b_col'],
    activebackground=theme['b_hover'],
    highlightcolor=theme['b_hl_border'],
    highlightbackground=theme['b_hl_border'],
    highlightthickness=1,
)
if pm_status:
    pm_slider['troughcolor'] = '#20ff20'
else:
    pm_slider['troughcolor'] = '#c10000'

pm_slider.set(int(pm_status))
pm_slider.grid(row=1, column=1, sticky=W)

recording = True
record_data()
mainloop()
