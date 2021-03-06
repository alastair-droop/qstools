#! /usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from enum import Enum
from os import listdir
from os.path import join, expandvars, splitext, abspath, dirname
import re
from sys import exit

# Get the version:
version = {}
with open(join(abspath(dirname(__file__)), 'version.py')) as f: exec(f.read(), version)

def main():
    # Set up the command line arguments & parse them:
    parser = argparse.ArgumentParser(description = 'Summarise qsubsec job log files')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument('-l', '--list', dest='list', action='store_true', help='list log files')
    parser.add_argument('-d', '--show-data', dest='show_data', action='store_true', help='output log data')
    action_group = parser.add_mutually_exclusive_group(required=False)
    action_group.add_argument('-r', '--list-running', dest='list_running', action='store_true', help='only list running samples')
    action_group.add_argument('-f', '--list-failed', dest='list_failed', action='store_true', help='only list failed samples')
    action_group.add_argument('-c', '--list-completed', dest='list_completed', action='store_true', help='only list completed samples')
    action_group.add_argument('-k', '--list-killed', dest='list_killed', action='store_true', help='only list killed samples')
    action_group.add_argument('-u', '--list-unknown', dest='list_unknown', action='store_true', help='only list unknown samples')
    parser.add_argument(dest='files', nargs='+', metavar='<logs>', help='log files')
    args = parser.parse_args()

    class status(Enum):
    	unknown = 'unknown'
    	running = 'running'
    	completed = 'completed'
    	failed = 'failed'
    	killed = 'killed'

    # Parse a log file:
    def parseLog(filename):
    	line = ''
    	with open(filename, 'rt') as file_handle:
    		for line in file_handle: pass
    	log_status = status.unknown
    	if 'completed' in line: log_status = status.completed
    	if 'started' in line: log_status = status.running
    	if 'failed' in line: log_status = status.failed
    	if ('imminent SIGSTOP' in line) or ('imminent SIGKILL' in line): log_status = status.killed 
    	return (filename, line.strip(), log_status)

    # Print a log file entry:
    def printSample(sample):
    	if args.show_data == True: print('{{:{}}}\t{{}}'.format(sample_nmax).format(sample[0], sample[1]))
    	else: print(sample[1])

    # Read in all the files in the given directory that match the given data:
    file_data = []
    totals = {status.running:0, status.completed:0, status.failed:0, status.killed:0, status.unknown:0}
    sample_nmax = 0
    for filename in args.files:
            sample_data = parseLog(filename)
            file_data.append(sample_data)
            totals[sample_data[2]] += 1
            sample_nmax = max(sample_nmax, len(str(filename)))
    # Report the data:
    if args.list == True:
        for f_dat in file_data:
            sample_status = f_dat[2]
            if (args.list_running == True) and (sample_status != status.running): continue
            if (args.list_failed == True) and (sample_status != status.failed): continue
            if (args.list_completed == True) and (sample_status != status.completed): continue
            if (args.list_killed == True) and (sample_status != status.killed): continue
            if (args.list_unknown == True) and (sample_status != status.unknown): continue
            printSample(f_dat)
    else:
        for status_type in (status.running, status.completed, status.failed, status.killed, status.unknown):
            print('{:9} {}'.format(status_type.name, totals[status_type]))
        print('{:9} {}'.format('TOTAL', sum([totals[i] for i in totals.keys()])))

# If run as main, run main():
if __name__ == '__main__': main()
