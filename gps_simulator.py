#!/usr/local/bin/python3

import argparse
import csv
import datetime
from numpy import arange
import pynmea2
from scipy.interpolate import interp1d
from time import sleep


def csv_columns_to_lists(csv_reader):
    first_line = next(csv_reader)
    columns = [[field] for field in first_line]

    for row in csv_reader:
        for i, field in enumerate(row):
            columns[i].append(field)

    return columns


def cast_csv_extracted_types(times, latitudes, longitudes, altitudes):
    times = [int(time) for time in times]
    latitudes = [float(lat) for lat in latitudes]
    longitudes = [float(lng) for lng in longitudes]
    altitudes = [float(alt) for alt in altitudes]
    return times, latitudes, longitudes, altitudes


def time_match_frequency(times, frequency):
    basic_time_period = times[1] - times[0]
    margin = 1/frequency if frequency >= 1 else 1
    return tuple(arange(times[0], times[-1] + margin, 1/frequency))
    

def interpolate(x, y, x_extended):
    f_interpolated = interp1d(x, y)
    return f_interpolated(x_extended)


def interpolate_coordinates(times, times_extended, lats, lngs, alts):
    lats_extended = interpolate(times, lats, times_extended)
    lngs_extended = interpolate(times, lngs, times_extended)
    alts_extended = interpolate(times, alts, times_extended)
    return lats_extended, lngs_extended, alts_extended


def timestamp_to_gpstime(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%H%M%S')


def latitude_to_hemisphere(coordinate):
    hemisphere = 'N' if coordinate >= 0 else 'S'
    return hemisphere
 
   
def longitude_to_hemisphere(coordinate):
    hemisphere = 'E' if coordinate >= 0 else 'W'
    return hemisphere


def simulate(times, freq, lats, lngs, alts, baudrate, tty):
    for time, lat, lng, alt in zip(times, lats, lngs, alts):
        msg = ('GP', 'GGA', (timestamp_to_gpstime(time), 
                            str(abs(lat)), latitude_to_hemisphere(lat),
                            str(abs(lng)), longitude_to_hemisphere(lng),
                            '1', '04', '2.6', str(alt), 'M',
                            '-33.9', 'M', '', '0000'))
        
        msg = pynmea2.GGA(*msg)
        print(str(msg))
        sleep(1/freq)


def main(flight_path_file, baudrate, tty, freq):
    with open(flight_path_file) as csvfile:
        flight_path_reader = csv.reader(csvfile, delimiter=',')
        (times, lats, lngs, alts) = csv_columns_to_lists(flight_path_reader)

    times, lats, lngs, alts = cast_csv_extracted_types(times, lats, lngs, alts)
    times_extended = time_match_frequency(times, args.frequency)
    lats, lngs, alts = interpolate_coordinates(times, times_extended, lats, lngs, alts)
    simulate(times, freq, lats, lngs, alts, baudrate, tty)


if __name__ == '__main__':
    APP_DESCRIPTION = 'GPS simulator, that takes a flight path in form of a \
                       csv file and outputs NMEA messages accordingly on a \
                       serial port.'
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)

    parser.add_argument('flight_path_file',
                        help='path to the flight path csv file')
    parser.add_argument('-b', '--baudrate', action='store', type=int,
                        default=9600, help='output serial baudrate (bps)')
    parser.add_argument('-t', '--tty', action='store', default='ttyUSB0',
                        help='filename for desired usb tty output')
    parser.add_argument('-f', '--frequency', action='store', default=1,
                        type=float,
                        help='frequency of simulated NMEA messages (Hz)')

    args = parser.parse_args()
    main(args.flight_path_file, args.baudrate, args.tty, args.frequency)
