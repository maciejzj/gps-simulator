#!/usr/bin/python

import argparse
#import serial
from scipy.interpolate import interp1d
import csv

def csv_columns_to_lists(csv_reader):
    first_line = csv_reader.next()
    columns = [[field] for field in first_line]

    for row in flight_path_reader:
        for i, field in enumerate(row):
            columns[i].append(field)

    return columns


def time_match_baudrate(time, baudrate):
    pass

def interpolate_coordinates(time, latitude, longitude):
    pass

def simulate(time, latitude, longitude, baudrate, tty):
    pass

APP_DESCRIPTION = 'GPS simulator, that takes a flight path in form of a csv \
                   file and outputs NMEA messages accordingly on a serial \
                   port.'
parser = argparse.ArgumentParser(description=APP_DESCRIPTION)

parser.add_argument('flight_path_file',
                    help='path to the flight path csv file')
parser.add_argument('-b', '--baudrate', action='store', default=9600,
                    help='output serial baudrate')
parser.add_argument('-t', '--tty', action='store', default='ttyUSB0',
                    help='filename for desired usb tty output')

args = parser.parse_args()

with open(args.flight_path_file) as csvfile:
    flight_path_reader = csv.reader(csvfile, delimiter=',')
    columns = csv_columns_to_lists(flight_path_reader)
