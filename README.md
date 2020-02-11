# GPS-simualtor

GPS simulator, that takes a path in form of a csv file and outputs NMEA
messages accordingly on a serial port.
Built to aid high alititude baloons hardware tests.
[This](https://predict.habhub.org) website can generate flight data file
compatible with the simulator.

## Prerequisites

You need Python 3 to run this scipt, dependencies are listed in the
`requirements.txt` file. You can install the with 
`pip3 install -r requirements.txt`.

## Usage

You can run the scipt with Python or directly as an executable if your
system matches the shebang path.

`python3 -m ps_simulator.py [-h] [-b BAUDRATE] [-t TTY] [-f FREQUENCY] [-d] [-V]
flight_path_file`

Positional arguments:

* `flight_path_file` path to the flight path csv file, the columns has to
   be: unix_timestamp, latitude, longitude altitude, (in ISO 6709 string
   Annex H format) without coulumns headers.

Optional arguments:

* `-h, --help ` show this help message and exit
* `-b BAUDRATE, --baudrate BAUDRATE` output serial baudrate (bps)
* `-t TTY, --tty TTY` file path for desired usb tty output
* `-f FREQUENCY, --frequency FREQUENCY` frequency of simulated NMEA
   messages (Hz)
* `-d, --dump` dump NMEA messages to file instead of sending them to
   serial
* `-V, --verbose` print NMEA messages to screen before sending
