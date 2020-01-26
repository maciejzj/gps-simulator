#!/usr/local/bin/python3

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
    print('\nProgram intertupted, closing...')
    sys.exit(0)


def csv_columns_to_lists(csv_reader):
    first_line = next(csv_reader)
    columns = [[field] for field in first_line]

    for row in csv_reader:
        for i, field in enumerate(row):
            columns[i].append(field)

    return columns


def parse_time(time):
    time = int(time)
    if time < 0:
        raise ValueError('Invalid timestamp in the given file, time cannot be \
                          a negative number')
    return time

def parse_coordinate(coord):
    coord = float(coord)
    if coord < -1800000 or coord > 1800000:
        raise ValueError('Invalid coordinate in the given file, latitude and \
                          longitude absolute value cannot exceed 180 degrees.')
    return coord


def parse_altitude(alt):
    alt = float(alt)
    return alt
    

def cast_csv_extracted_types(times, latitudes, longitudes, altitudes):
    times = [parse_time(time) for time in times]
    latitudes = [parse_coordinate(lat) for lat in latitudes]
    longitudes = [parse_coordinate(lng) for lng in longitudes]
    altitudes = [parse_altitude(alt) for alt in altitudes]
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


def build_nmea_GPGGA_string(time, lat, lng, alt):
    msg = ('GP', 'GGA', (timestamp_to_gpstime(time), 
                        str(abs(lat)), latitude_to_hemisphere(lat),
                        str(abs(lng)), longitude_to_hemisphere(lng),
                        '1', '04', '2.6', str(alt), 'M',
                        '-33.9', 'M', '', '0000'))
    return pynmea2.GGA(*msg)


def simulate(times, freq, lats, lngs, alts, ser):
    for time, lat, lng, alt in zip(times, lats, lngs, alts):
        msg = build_nmea_GPGGA_string(time, lat, lng, alt)
        if VERBOSE == True:
            print(str(msg))
        sleep(1/freq)
        
        
def extract_flight_data_from_csv(flight_path_file):
    with open(flight_path_file) as csvfile:
        flight_path_reader = csv.reader(csvfile, delimiter=',')
        times, lats, lngs, alts = csv_columns_to_lists(flight_path_reader)
    return times, lats, lngs, alts


def main(flight_path_file, baudrate, tty, freq):
    times, lats, lngs, alts = extract_flight_data_from_csv(flight_path_file)
    
    ser = serial.Serial(tty, baudrate=baudrate)

    times, lats, lngs, alts = cast_csv_extracted_types(times, lats, lngs, alts)
    times_extended = time_match_frequency(times, args.frequency)
    lats, lngs, alts = interpolate_coordinates(times, times_extended, lats, lngs, alts)
    
    simulate(times, freq, lats, lngs, alts, None)
    
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
    parser.add_argument('-b', '--baudrate', action='store', type=int,
                        default=9600, help='output serial baudrate (bps)')
    parser.add_argument('-t', '--tty', action='store', default='/dev/ttyUSB0',
                        help='file path for desired usb tty output')
    parser.add_argument('-f', '--frequency', action='store', default=1,
                        type=float,
                        help='frequency of simulated NMEA messages (Hz)')
    parser.add_argument('-V', '--verbose', action='store_true',
                        default='false',
                        help='pint NMEA messages to screen before sending')

    args = parser.parse_args()
    VERBOSE = args.verbose
    main(args.flight_path_file, args.baudrate, args.tty, args.frequency)
