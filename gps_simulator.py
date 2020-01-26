#!/usr/bin/python

import argparse
import csv
from numpy import arange
from scipy.interpolate import interp1d


def csv_columns_to_lists(csv_reader):
    first_line = csv_reader.next()
    columns = [[field] for field in first_line]

    for row in flight_path_reader:
        for i, field in enumerate(row):
            columns[i].append(field)

    return columns


def cast_csv_extracted_types(times, latitudes, longitudes, altitudes):
    times = [int(time) for time in times]
    latitudes = (float(lat) for lat in latitudes)
    longitudes = (float(lng) for lng in longitudes)
    altitudes = (float(alt) for alt in altitudes)
    return times, latitudes, longitudes, altitudes


def time_match_frequency(times, frequency):
    basic_time_period = times[1] - times[0]
    return tuple(arange(times[0], times[-1], 1/frequency))


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
                    help='output serial baudrate (bps)')
parser.add_argument('-t', '--tty', action='store', default='ttyUSB0',
                    help='filename for desired usb tty output')
parser.add_argument('-f', '--frequency', action='store', default=1,
                    help='frequency of simulated NMEA messages (Hz)')

args = parser.parse_args()

with open(args.flight_path_file) as csvfile:
    flight_path_reader = csv.reader(csvfile, delimiter=',')
    (times, lats, lngs, alts) = csv_columns_to_lists(flight_path_reader)

(times, lats, lngs, alts) = cast_csv_extracted_types(times, lats, lngs, alts)
times = time_match_frequency(times, args.frequency)
