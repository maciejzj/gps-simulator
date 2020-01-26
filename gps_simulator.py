#!/usr/local/bin/python3
'''
Executable for simulating GPS NEMA messaging in time, with given data.
Built to simulate high altitide balloon flights for hardware testing.
Run this program with `-h` to see help.
'''

import argparse
import csv
import datetime
import signal
import sys
from time import sleep

from numpy import arange
import pynmea2
from scipy.interpolate import interp1d
import serial


def signal_handler(sig, frame):
    '''Handle UNIX system signals.'''

    if sig == signal.SIGINT:
        handle_sigint()


def handle_sigint():
    '''Handle UNIX system SIGINT signal.'''

    print('\nProgram intertupted, closing...')
    sys.exit(0)


def csv_columns_to_lists(csv_reader):
    '''
    Extract csv coluns in form of lists, returns lists of lists of columns
    contents.
    '''

    first_line = next(csv_reader)
    columns = [[field] for field in first_line]

    for row in csv_reader:
        for (i, field) in enumerate(row):
            columns[i].append(field)

    return columns


def parse_time(time):
    '''
    Parse timestamp string extracted from file and cast it to number, the
    timestamp has to be in the UNIX universal time format.
    '''

    time = int(time)
    if time < 0:
        raise ValueError('Invalid timestamp in the given file, time cannot be \
                          a negative number')
    return time


def parse_coordinate(coord):
    '''
    Parse latitude or longitude coordinate string extracted from file and
    cast it to number, the coordinates has to be in the ISO 6709 string Annex
    H format.
    '''

    coord = float(coord)
    if coord < -1800000 or coord > 1800000:
        raise ValueError('Invalid coordinate in the given file, latitude and \
                          longitude absolute value cannot exceed 180 degrees.')
    return coord


def parse_altitude(alt):
    '''Parse altitude string extracted from file and cast to number.'''

    alt = float(alt)
    return alt


def parse_flight_data(times, lats, lngs, alts):
    '''
    Parse flight data strings extracted from file and return in numerical
    format.
    '''

    times = [parse_time(time) for time in times]
    lats = [parse_coordinate(lat) for lat in lats]
    lngs = [parse_coordinate(lng) for lng in lngs]
    alts = [parse_altitude(alt) for alt in alts]
    return (times, lats, lngs, alts)


def interpolate_times_to_frequency(times, frequency):
    '''Interpolate linear space of timestamps to match given frequency.'''

    basic_time_period = times[1] - times[0]
    margin = (1 / frequency if frequency >= 1 else 1)
    return tuple(arange(times[0], times[-1] + margin, 1 / frequency))


def interpolate(x, y, x_extended):
    '''
    Interpolate given f(x) = y function to fill missing data for denser
    x_extended domain.
    '''

    f_interpolated = interp1d(x, y)
    return f_interpolated(x_extended)


def interpolate_coordinates(times, times_extended, lats, lngs, alts):
    '''Interpolate GPS data to fill missing data for denser time domain.'''

    lats_extended = interpolate(times, lats, times_extended)
    lngs_extended = interpolate(times, lngs, times_extended)
    alts_extended = interpolate(times, alts, times_extended)
    return (lats_extended, lngs_extended, alts_extended)


def timestamp_to_gpstime(timestamp):
    '''
    Parse universal UNIX timestamp into hoursminutesseconds string used in
    GPS GPGGA messages.
    '''

    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%H%M%S')


def latitude_to_hemisphere(coordinate):
    '''
    Extract hemisphere char 'N'/'S' symbol for latitude given in the ISO 6709
    string Annex H format.
    '''

    hemisphere = ('N' if coordinate >= 0 else 'S')
    return hemisphere


def longitude_to_hemisphere(coordinate):
    '''
    Extract hemisphere char 'W'/'E' symbol for longitude given in the ISO 6709
    string Annex H format.
    '''

    hemisphere = ('E' if coordinate >= 0 else 'W')
    return hemisphere


def build_nmea_gpgaa_string(time, lat, lng, alt):
    '''
    Build NEMA GPGAA message string from given UNIX universal time timestamp,
    latitude and longitude in the ISO 6709 string Annex H format and altiitude
    in meters above the sea level.
    '''

    msg = ('GP', 'GGA', (timestamp_to_gpstime(time),
                         str(abs(lat)), latitude_to_hemisphere(lat),
                         str(abs(lng)), longitude_to_hemisphere(lng),
                         '1', '01', '1.0',  # Fix quality, satelites num, HDOP
                         str(alt), 'M',
                         '0', 'M',  # Height of geoid above WGS84 ellipsoid
                         '', '0000'))  # Time since DGPS last update and id
    return pynmea2.GGA(*msg)


def simulate(times, freq, lats, lngs, alts, ser):
    '''
    Simulate the GPS messanging according to given data and ouptut NMEA
    messages on serial port.

    :param times: List of timestamps sent to send during simulated flight
    :param freq" Frequency of sending the simulated NMEA GPS messages
    :param lats: List of latitude coordinates to send (in ISO 6709
                string Annex H format)
    :param lngs: List of longitude coordinates to send (in ISO 6709
                string Annex H format)
    :param alts: List of altitude coordinates to send (meters above the sea
                level)
    :param ser: Serial port to which the simulated NMEA GPS messages will be
                written to
    '''

    for (time, lat, lng, alt) in zip(times, lats, lngs, alts):
        msg = build_nmea_gpgaa_string(time, lat, lng, alt)
        if VERBOSE is True:
            print(str(msg))
        sleep(1 / freq)


def extract_flight_data_from_csv(flight_path_file):
    '''Read the flight data from given csv file.'''

    with open(flight_path_file) as csvfile:
        flight_path_reader = csv.reader(csvfile, delimiter=',')
        (times, lats, lngs, alts) = csv_columns_to_lists(flight_path_reader)
    return (times, lats, lngs, alts)


def main(flight_path_file, baudrate, tty, freq):
    '''
    Main function for the simulator, reads and prepares flight data from csv
    file, performs the simulation and outputs NEMA GPS messages to the serial
    port on given tty.
    '''

    (times, lats, lngs, alts) = extract_flight_data_from_csv(flight_path_file)

    (times, lats, lngs, alts) = parse_flight_data(times, lats, lngs, alts)
    times_extended = interpolate_times_to_frequency(times, args.frequency)
    (lats, lngs, alts) = interpolate_coordinates(times, times_extended,
                                                 lats, lngs, alts)

    ser = serial.Serial(tty, baudrate=baudrate)

    simulate(times_extended, freq, lats, lngs, alts, ser)

    ser.close()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    APP_DESCRIPTION = 'GPS simulator, that takes a flight path in form of a \
                       csv file and outputs NMEA messages accordingly on a \
                       serial port.'
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)

    parser.add_argument('flight_path_file',
                        help='path to the flight path csv file, the columns \
                        has to be: unix_timestamp, latitude, longitude \
                        altitude, (in ISO 6709 string Annex H format) \
                        without coulumns headers')
    parser.add_argument('-b', '--baudrate', action='store',
                        type=int, default=9600,
                        help='output serial baudrate (bps)')
    parser.add_argument('-t', '--tty', action='store',
                        default='/dev/ttyUSB0',
                        help='file path for desired usb tty output')
    parser.add_argument('-f', '--frequency', action='store',
                        type=float, default=1,
                        help='frequency of simulated NMEA messages (Hz)')
    parser.add_argument('-V', '--verbose', action='store_true',
                        default='false',
                        help='pint NMEA messages to screen before sending')

    args = parser.parse_args()
    VERBOSE = args.verbose
    main(args.flight_path_file, args.baudrate, args.tty, args.frequency)
