#!/usr/bin/python

import argparse
#import serial
from scipy.interpolate import interp1d
import csv

APP_DESCRIPTION = 'GPS simulator, that takes flight path in a form of csv file \
                   and outputs NMEA messages accordingly on a serial port.'
parser = argparse.ArgumentParser(description=APP_DESCRIPTION)

parser.add_argument('flight_path_file',
                    help='path to the flight path csv file')
parser.add_argument('-b', '--baudrate', action='store', default=9600,
                    help='output serial baudrate')
parser.add_argument('-t', '--tty', action='store', default='ttyUSB0',
                    help='filename for desired usb tty output')

args = parser.parse_args()

def csv_flight_path_to_lists(csv_reader):
    pass
    
def time_match_baudrate(time, baudrate):
    pass
    
def interpolate_coordinates(time, latitude, longitude):
    pass
    
def simulate(time, latitude, longitude, baudrate, tty):
    pass
			