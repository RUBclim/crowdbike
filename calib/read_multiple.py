import time
from datetime import datetime
from datetime import timezone

import sentry_sdk
from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_driver.linux_i2c_transceiver import LinuxI2cTransceiver
from sensirion_i2c_sht.sht3x import Sht3xI2cDevice

sentry_sdk.init(
    dsn='https://8d1142f8badf4bb2a52e1744b23b2920@o1323140.ingest.sentry.io/6584968',  # noqa: E501
    traces_sample_rate=0,
)

# map the sensor id to the device address provided by the i2c multiplexer
SENSORS = {
    '42': Sht3xI2cDevice(I2cConnection(LinuxI2cTransceiver('/dev/i2c-22'))),
    '45': Sht3xI2cDevice(I2cConnection(LinuxI2cTransceiver('/dev/i2c-23'))),
    '59': Sht3xI2cDevice(I2cConnection(LinuxI2cTransceiver('/dev/i2c-24'))),
    # add more if needed
}

FILENAME = 'crowdbike_calibration.csv'

while True:
    for sensor_nr, sensor in SENSORS.items():
        temp, hum = sensor.single_shot_measurement()
        serial_nr = sensor.read_serial_number()
        now = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        csv_str = (
            f'{now},{temp.degrees_celsius},{hum.percent_rh},'
            f'{sensor_nr},{serial_nr}'
        )
        with open(FILENAME, 'a') as f:
            f.write(f'{csv_str}\n')

    time.sleep(1)
