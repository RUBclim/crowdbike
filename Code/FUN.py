import serial
import socket
from numpy import nan

def get_ip():
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

def read_pm(dev, baudrate=9600):
    '''
    function for reading the Nova-PM-sensor
    dev must be type <str> e.g. '/dev/ttyUSB0'
    function from https://gist.github.com/marw/9bdd78b430c8ece8662ec403e04c75fe
    '''
    # define serial port
    try:
        ser = serial.Serial()
        ser.port = dev
        ser.baudrate = baudrate

        # open connection
        if not ser.isOpen():
            ser.open()
        
        # read data
        bytes = ser.read(10)
        assert bytes[0] == ord(b'\xaa')
        assert bytes[1] == ord(b'\xc0')
        assert bytes[9] == ord(b'\xab')

        pm2_5 = (bytes[3]*256+bytes[2])/10.0
        pm10 = (bytes[5]*256+bytes[4])/10.0

        checksum = sum(v for v in bytes[2:8]) % 256
        assert checksum == bytes[8]

        measures = {'PM10': pm10, 'PM2_5': pm2_5}

        ser.close()
        return(measures)
    except:
        measures = {'PM10': nan, 'PM2_5': nan}
        return measures