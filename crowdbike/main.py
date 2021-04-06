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

import numpy as np
import RPi.GPIO as GPIO
from tkinter import Button
from tkinter import DISABLED
from tkinter import E
from tkinter import HORIZONTAL
from tkinter import Label
from tkinter import mainloop
from tkinter import NORMAL
from tkinter import Scale
from tkinter import Tk
from tkinter import W

from crowdbike.helpers import get_ip
from crowdbike.helpers import get_wlan_macaddr
from crowdbike.helpers import sat_vappressure
from crowdbike.helpers import setup_config
from crowdbike.helpers import vappressure
from crowdbike.sensors import DHT22
from crowdbike.sensors import GPS
from crowdbike.sensors import PmSensor
from crowdbike.sensors import SHT85


class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status: int = 0, message: Optional[str] = None) -> NoReturn:
        GPIO.cleanup()
        if message:
            self._print_message(message, sys.stderr)
        exit(status)


parser = ArgumentParser()
parser.add_argument('command', choices=['init', 'run'])
args = parser.parse_args()

if args.command == 'init':
    setup_config()
    GPIO.cleanup()
    exit(0)


# __load config files__
with open(os.path.join(os.path.dirname(__file__), 'config.json')) as cfg:
    config = json.load(cfg)

raspberryid = config['user']['bike_nr']  # number of your pi
studentname = config['user']['studentname']
mac = get_wlan_macaddr()

with open(os.path.join(os.path.dirname(__file__), 'calibration.json')) as cal:
    calib = json.load(cal)

# __calibration params__
temperature_cal_a1 = calib['temp_cal_a1']
temperature_cal_a0 = calib['temp_cal_a0']
hum_cal_a1 = calib['hum_cal_a1']
hum_cal_a0 = calib['hum_cal_a0']

window_title = f'Crowdbike {raspberryid}'
logfile_path = config['user']['logfile_path']
os.makedirs(logfile_path, exist_ok=True)

logfile_name = f'{raspberryid}_{studentname}_{datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")}.csv'  # noqa E501
logfile = os.path.join(logfile_path, logfile_name)

counter = 0

# initialize threads
gpsp = GPS()
gpsp.start()

temp_hum_sensor: Union[DHT22, SHT85]
sensor_type = config['user']['sensor_type']
if sensor_type == 'SHT85':
    temp_hum_sensor = SHT85()
elif sensor_type == 'DHT22':
    temp_hum_sensor = DHT22()
else:
    raise NameError('sensor type unknown, must be either SHT85 or DHT22')

temp_hum_sensor.start()
nova_pm = PmSensor(dev='/dev/ttyUSB0')

# global variables
font_size = 24
recording = False

pm_status = nova_pm.running = config['user']['pm_sensor']
# switch off sensor if it running prior to starting the app
if pm_status is False:
    nova_pm.sensor_sleep()

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
    master.destroy()
    gpsp.running = False
    gpsp.stop()
    gpsp.join()
    temp_hum_sensor.running = False
    temp_hum_sensor.join()
    nova_pm.running = False
    # only try joining the thread it was running
    if nova_pm.isAlive():
        nova_pm.join()
    GPIO.cleanup()
    exit(0)


def record_data() -> None:
    global recording
    recording = True
    b2.config(state=NORMAL)
    b1.config(state=DISABLED)

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
    b1.config(state=NORMAL)
    b2.config(state=DISABLED)


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
            nova_pm = PmSensor(dev='/dev/ttyUSB0')
            nova_pm.running = True
            nova_pm.start()
        except Exception:
            pass
    else:
        pm_status = False
        pm_slider['troughcolor'] = '#c10000'
        try:
            nova_pm.running = False
            nova_pm.join()
            nova_pm.sensor_sleep()
        except Exception:
            pass


def start_counting(label: Label) -> None:
    counter = 0

    def count() -> None:
        global counter
        counter += 1
        computer_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # get sensor readings from DHT-sensor
        try:
            humidity = temp_hum_sensor.humidity or np.nan
            temperature = temp_hum_sensor.temperature or np.nan
        except Exception:
            humidity = np.nan
            temperature = np.nan

        # dht22_humidity = readings['humidity']
        # dht22_temperature = readings['temperature']

        # calculate temperature with sensor calibration values
        temperature_raw = round(temperature, 5)
        temperature_calib = round(
            temperature /
            temperature_cal_a1 -
            temperature_cal_a0, 3,
        )

        humidity_raw = round(humidity, 5)
        humidity_calib = round(
            humidity /
            hum_cal_a1 -
            hum_cal_a0, 3,
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
            pm2_5 = np.nan
            pm10 = np.nan

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
            f0 = open(logfile, 'a')
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

            f0.close()
    count()


# define widgets
master = Tk()
master.title(window_title)
# master.attributes('-fullscreen', True)
Label(
    master, text=' Name', fg='blue',
    font=('Helvetica', font_size),
).grid(row=0, column=0, sticky=W)
Label(
    master, text=studentname + "'s Crowdbike", fg='blue',
    font=('Helvetica', font_size),
).grid(
    row=0, column=1, sticky=W,
    columnspan=2,
)
Label(
    master, text=' IP', fg='blue',
    font=('Helvetica', font_size),
).grid(row=2, column=0, sticky=W)
Label(
    master, text=str('IP: ' + get_ip()), fg='blue',
    font=('Helvetica', font_size),
).grid(
    row=1, column=2, sticky=E,
    columnspan=2,
)
Label(
    master, text=' PM-Sensor', fg='blue',
    font=('Helvetica', font_size),
).grid(
    row=1, column=0, sticky=W,
    columnspan=2,
)

# define labels
label_counter = Label(
    master, text=' Counter',
    font=('Helvetica', font_size),
)
label_counter.grid(row=2, column=0, sticky=W)

label_ctime = Label(master, text=' Time', font=('Helvetica', font_size))
label_ctime.grid(row=3, column=0, sticky=W)

label_altitude = Label(
    master, text=' Altitude',
    font=('Helvetica', font_size),
)
label_altitude.grid(row=4, column=0, sticky=W)

label_latitude = Label(
    master, text=' Latitude',
    font=('Helvetica', font_size),
)
label_latitude.grid(row=5, column=0, sticky=W)

label_longitude = Label(
    master, text=' Longitude',
    font=('Helvetica', font_size),
)
label_longitude.grid(row=6, column=0, sticky=W)

label_speed = Label(master, text=' Speed', font=('Helvetica', font_size))
label_speed.grid(row=7, column=0, sticky=W)

label_time = Label(master, text=' GPS Time', font=('Helvetica', font_size))
label_time.grid(row=8, column=0, sticky=W)

label_temperature = Label(
    master, text=' Temperature',
    font=('Helvetica', font_size),
)
label_temperature.grid(row=9, column=0, sticky=W)

label_humidity = Label(
    master, text=' Rel. Humidity',
    font=('Helvetica', font_size),
)
label_humidity.grid(row=10, column=0, sticky=W)

label_vappress = Label(
    master, text=' Vap. Pressure   ',
    font=('Helvetica', font_size),
)
label_vappress.grid(row=11, column=0, sticky=W)

# labels for pm sensor
label_pm10 = Label(master, text=' PM 10 ', font=('Helvetica', font_size))
label_pm10.grid(row=12, column=0, sticky=W)

label_pm2_5 = Label(master, text=' PM 2.5 ', font=('Helvetica', font_size))
label_pm2_5.grid(row=13, column=0, sticky=W)

# define values (constructed also as labels, text will be modified in count)
value_counter = Label(
    master, text=' Counter', bg='red',
    font=('Helvetica', font_size),
)
value_counter.grid(row=2, column=1, sticky=W, columnspan=2)

value_ctime = Label(master, text=' Time', font=('Helvetica', font_size))
value_ctime.grid(row=3, column=1, sticky=W, columnspan=2)

value_altitude = Label(
    master, text=' Altitude',
    font=('Helvetica', font_size),
)
value_altitude.grid(row=4, column=1, sticky=W, columnspan=2)

value_latitude = Label(
    master, text=' Latitude',
    font=('Helvetica', font_size),
)
value_latitude.grid(row=5, column=1, sticky=W, columnspan=2)

value_longitude = Label(
    master, text=' Longitude',
    font=('Helvetica', font_size),
)
value_longitude.grid(row=6, column=1, sticky=W, columnspan=2)

value_speed = Label(
    master, text=' Speed',
    font=('Helvetica', font_size),
)

value_speed.grid(row=7, column=1, sticky=W, columnspan=2)

value_time = Label(
    master, text='GPS Time ---------------',
    font=('Helvetica', font_size),
)
value_time.grid(row=8, column=1, sticky=W, columnspan=2)

value_temperature = Label(
    master, text=' Temperature',
    font=('Helvetica', font_size),
)
value_temperature.grid(row=9, column=1, sticky=W, columnspan=2)

value_humidity = Label(
    master, text=' Rel. Humidity',
    font=('Helvetica', font_size),
)
value_humidity.grid(row=10, column=1, sticky=W, columnspan=2)

value_vappress = Label(
    master, text=' Vap. Pressure ',
    font=('Helvetica', font_size),
)
value_vappress.grid(row=11, column=1, sticky=W, columnspan=2)

value_pm10 = Label(master, text=' PM 10 ', font=('Helvetica', font_size))
value_pm10.grid(row=12, column=1, sticky=W, columnspan=2)
value_pm2_5 = Label(master, text=' PM 2.5 ', font=('Helvetica', font_size))
value_pm2_5.grid(row=13, column=1, sticky=W, columnspan=2)

# initialize value_counter
start_counting(value_counter)

# define buttons
b1 = Button(
    master, text='Record', width=7, state=DISABLED,
    command=record_data,
)
b1.grid(row=15, column=0, sticky=W)

b2 = Button(master, text='Stop', width=7, state=DISABLED, command=stop_data)
b2.grid(row=15, column=1, sticky=W)

b4 = Button(master, text='Exit', width=7, state=NORMAL, command=exit_program)
b4.grid(row=15, column=2, sticky=W)

# slider
pm_slider = Scale(
    orient=HORIZONTAL, length=80, to=1, label='',
    showvalue=False, sliderlength=40, troughcolor='#666666',
    width=30, command=set_pm_status,
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
