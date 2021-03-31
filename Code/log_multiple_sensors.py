import argparse
import csv
import signal
import time
from datetime import datetime
from typing import Tuple

import adafruit_dht
import board
from numpy import nan
from retry import retry

FILENAME = '/home/pi/crowdbike/logs/calibration_measurements_'\
    f'{datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")}.csv'

# Define the GPIO for each sensor
# The key is the sensor label
# board.D\xy is the GPIO pin number
SENSORS = {
    'sensor_6':  adafruit_dht.DHT22(board.D17),
    'sensor_12': adafruit_dht.DHT22(board.D4),
    # 'sensor_13': adafruit_dht.DHT22(board.D18),
    'sensor_14': adafruit_dht.DHT22(board.D27),
    # 'sensor_15': adafruit_dht.DHT22(board.D23),
    'sensor_16': adafruit_dht.DHT22(board.D22),
    # 'sensor_17': adafruit_dht.DHT22(board.D24),
    # 'sensor_18': adafruit_dht.DHT22(board.D25),
    # 'sensor_19': adafruit_dht.DHT22(board.D5),
    # 'sensor_20': adafruit_dht.DHT22(board.D6),
    # 'sensor_21': adafruit_dht.DHT22(board.D12),
    # 'sensor_22': adafruit_dht.DHT22(board.D13),
}

parser = argparse.ArgumentParser(
    prog='calib_sensors',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    '-v', '--verbose',
    help='increase verbosity',
    action='store_true',
)
args = parser.parse_args()

HEADER = [
    'date',
    'temp',
    'hum',
    'sensor_id',
]


@retry(tries=5)
def read_dht22(sensor: adafruit_dht.DHT22) -> Tuple[float, float]:
    temp = sensor.temperature
    hum = sensor.humidity
    if temp is None:
        temp = nan
    if hum is None:
        hum = nan
    return (temp, hum)


def write_header() -> None:
    with open(FILENAME, 'w') as f:
        writer = csv.DictWriter(f=f, fieldnames=HEADER)
        writer.writeheader()
    f.close()


def _exit_programm(signum, frame) -> None:  # type: ignore
    exit(0)


def main() -> None:
    write_header()
    while True:
        with open(FILENAME, 'a') as f:
            writer = csv.DictWriter(f=f, fieldnames=HEADER)
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            for sensor in SENSORS:
                readings = read_dht22(sensor=SENSORS[sensor])
                log = {
                    'date': timestamp,
                    'temp': readings[0],
                    'hum': readings[1],
                    'sensor_id': sensor,
                }
                time.sleep(1)
                if args.verbose:
                    print(log)
                    print(' done reading all sensors '.center(79, '*'))

                writer.writerow(rowdict=log)
            f.close()
            print(' next run '.center(79, '*'))


signal.signal(signal.SIGTERM, _exit_programm)

if __name__ == '__main__':
    main()
