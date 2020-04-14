# -*- coding: utf-8 -*-
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
import json
import os
from datetime import datetime
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

import adafruit_dht
import board
import numpy as np
from FUN import get_ip
from FUN import GPS
from FUN import pm_sensor
from FUN import read_dht22
# __load config files__
with open(
    os.path.join(
        os.path.dirname(__file__),
        'config.json',
    ), 'r',
) as config:
    config = json.load(config)

raspberryid = config['user']['bike_nr']  # number of your pi
studentname = config['user']['studentname']

with open(
    os.path.join(
        os.path.dirname(__file__),
        'calibration.json',
    ), 'r',
) as calib:
    calib = json.load(calib)

# __calibration params__
temperature_cal_a1 = calib['temp_cal_a1']
temperature_cal_a0 = calib['temp_cal_a0']
vappress_cal_a1 = calib['vappress_cal_a1']
vappress_cal_a0 = calib['vappress_cal_a0']

window_title = 'Crowdbike' + raspberryid
logfile_path = config['user']['logfile_path']
if not os.path.exists(logfile_path):
    os.makedirs(logfile_path)

logfile_name = f'{raspberryid}_{studentname}_{datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")}.csv'  # noqa E501
logfile = os.path.join(logfile_path, logfile_name)

# __global variables
font_size = 24
recording = False
pm_status = config['user']['pm_sensor']
sampling_rate = config['user']['sampling_rate']

# main program
counter = 0
gpsp = GPS()
gpsp.start()
dht22_sensor = adafruit_dht.DHT22(board.D4)
nova_pm = pm_sensor(dev='/dev/ttyUSB0')
cnames = [
    'ID',
    'Record',
    'Raspberry_Time',
    'GPS_Time',
    'Altitude',
    'Latitude',
    'Longitude',
    'Speed',
    'Temperature',
    'TemperatureRaw',
    'RelHumidity',
    'RelHumidityRaw',
    'VapourPressure',
    'VapourPressureRaw',
    'PM10',
    'PM2.5',
]


# __functions__
def exit_program() -> None:
    master.destroy()
    gpsp.running = False
    gpsp.stop()
    gpsp.join()
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
    if value == '1':
        pm_status = True
        pm_slider['troughcolor'] = '#20ff20'
        try:
            nova_pm.sensor_wake()
        except:
            pass
    else:
        pm_status = False
        pm_slider['troughcolor'] = '#c10000'
        try:
            nova_pm.sensor_sleep()
        except:
            pass


def start_counting(label: Label) -> None:
    counter = 0

    def count():
        global counter
        counter += 1
        computer_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # get sensor readings from DHT-sensor
        try:
            readings = read_dht22(dht22_sensor)
        except:
            dht22_humidity = np.nan
            dht22_temperature = np.nan

        dht22_humidity = readings['humidity']
        dht22_temperature = readings['temperature']

        # calculate temperature with sensor calibration values
        dht22_temperature_raw = round(dht22_temperature, 5)
        dht22_temperature_calib = round(
            dht22_temperature *
            temperature_cal_a1 +
            temperature_cal_a0, 3,
        )
        dht22_temperature = dht22_temperature_calib

        saturation_vappress_ucalib = (
                                      0.6113 * np.exp((2501000.0 / 461.5) *
                                                      ((1.0 / 273.15) -
                                                      (
                                                          1.0 / (
                                                              dht22_temperature_raw +  # noqa 501
                                                              273.15
                                                          )
                                                      )))
        )
        saturation_vappress_calib = (
                                      0.6113 * np.exp((2501000.0 / 461.5) *
                                                      ((1.0 / 273.15) -
                                                      (
                                                          1.0 / (
                                                              dht22_temperature_calib +  # noqa 501
                                                              273.15
                                                          )
                                                      )))
        )
        dht22_vappress = (
            (dht22_humidity / 100.0) * saturation_vappress_ucalib
        )
        dht22_vappress_raw = round(dht22_vappress, 3)
        dht22_vappress_calib = round(
            dht22_vappress *
            vappress_cal_a1 +
            vappress_cal_a0, 3,
        )
        dht22_vappress = dht22_vappress_calib

        dht22_humidity_raw = round(dht22_humidity, 5)
        dht22_humidity = round(
            100 * (
                dht22_vappress_calib /
                saturation_vappress_calib
            ), 5,
        )

        # read pm-sensor takes max 1 sec
        if pm_status is True:
            pm = nova_pm.read_pm()
            pm2_5 = pm['PM2_5']
            pm10 = pm['PM10']
        else:
            pm2_5 = np.nan
            pm10 = np.nan

        if dht22_humidity > 100:
            dht22_humidity = 100

        # Get GPS position
        gps_time = gpsp.timestamp
        gps_altitude = gpsp.alt
        gps_latitude = gpsp.latitude
        gps_longitude = gpsp.longitude
        gps_speed = round(gpsp.speed * 1.852, 2)

        f_mode = int(gpsp.satellites)  # store number of sats
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
        value_altitude.config(text='{0:.3f} m ASL'.format(gps_altitude))
        value_latitude.config(text='{0:.6f} °N'.format(gps_latitude))
        value_longitude.config(text='{0:.6f} °E'.format(gps_longitude))
        value_speed.config(text='{0:.1f} km/h'.format(gps_speed))
        value_time.config(text=gps_time)
        value_temperature.config(text='{0:.1f} °C'.format(dht22_temperature))
        value_humidity.config(text='{0:.1f} %'.format(dht22_humidity))
        value_vappress.config(text='{0:.3f} kPa'.format(dht22_vappress))

        value_pm10.config(text='{0:.1f} \u03BCg/m\u00B3'.format(pm10))
        value_pm2_5.config(text='{0:.1f} \u03BCg/m\u00B3'.format(pm2_5))

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

            f0.write('{0:.3f}'.format(gps_altitude) + ',')
            f0.write('{0:.6f}'.format(gps_latitude) + ',')
            f0.write('{0:.6f}'.format(gps_longitude) + ',')
            f0.write('{0:.1f}'.format(gps_speed) + ',')

            f0.write(str(dht22_temperature) + ',')
            f0.write(str(dht22_temperature_raw) + ',')

            f0.write(str(dht22_humidity) + ',')
            f0.write(str(dht22_humidity_raw) + ',')

            f0.write(str(dht22_vappress) + ',')
            f0.write(str(dht22_vappress_raw) + ',')

            f0.write(str(pm10) + ',')
            f0.write(str(pm2_5) + '\n')

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
    showvalue=False, sliderlength=40, troughcolor=None,
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
