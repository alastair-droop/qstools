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
import subprocess
from sys import exit
import xml.etree.ElementTree
import os.path

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.py')) as f: exec(f.read(), version)

def main():
    # Set up the command line arguments & parse them:
    parser = argparse.ArgumentParser(description = 'Display running qsub jobs')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(version['__version__']))
    parser.add_argument('-f', '--full', dest='full', action='store_true', default=False, help='display extended output')
    action_group = parser.add_mutually_exclusive_group(required=False)
    action_group.add_argument('-c', '--column-headers', dest='header', action='store_true', default=False, help='display header line on data')
    action_group.add_argument('-n', '--number', dest='count', action='store_true', default=False, help='display job counts, not data')
    args = parser.parse_args()

    def error(message): exit('ERROR: {}'.format(message))

    # Get the XML data from qstat:
    try: qstat_process = subprocess.Popen(args=['qstat', '-xml'], stdout=subprocess.PIPE, universal_newlines=True)
    except: error('failed to execute subprocess "qsubsec"')
    try: result = qstat_process.communicate(timeout=15)[0]
    except:
    	qstat_process.kill()
    	qstat_process.communicate()
    	error('failed to get job data from qsub')

    # Parse the output XML:
    try: xml_root = xml.etree.ElementTree.fromstring(result)
    except: error('failed to parse returned XML')

    # Extract job data:
    jobs = {}
    def addJob(job):
    	job_id = int(job.find('JB_job_number').text)
    	jobs[job_id] = {}
    	jobs[job_id]['id'] = job_id
    	jobs[job_id]['name'] = job.find('JB_name').text
    	jobs[job_id]['priority'] = float(job.find('JAT_prio').text)
    	jobs[job_id]['owner'] = job.find('JB_owner').text
    	jobs[job_id]['code'] = job.find('state').text
    	jobs[job_id]['state'] = job.attrib['state']
    	try: jobs[job_id]['start'] = job.find('JAT_start_time').text
    	except: jobs[job_id]['start'] = ''
    	jobs[job_id]['queue'] = job.find('queue_name').text
    	if jobs[job_id]['queue'] == None: jobs[job_id]['queue'] = ''
    	jobs[job_id]['slots'] = int(job.find('slots').text)
    for job_info in xml_root.findall('job_info'):
    	for job in job_info.findall('job_list'): addJob(job)
    for queue_info in xml_root.findall('queue_info'):
    	for job in queue_info.findall('job_list'): addJob(job)
	
    if args.count == True:
    	if args.full == False: print(len(jobs))
    	else:
    		totals = {}
    		max_len = 0
    		for job_id in jobs.keys():
    			state = jobs[job_id]['state']
    			if state not in totals.keys():
    				totals[state] = 1
    				max_len = max(max_len, len(state))
    			else: totals[state] += 1
    		for state in sorted(totals.keys()): print('{{:{}}}\t{{}}'.format(max_len).format(state, totals[state]))
    else:
    	if len(jobs) != 0:	
    		if args.full == False: columns = ('id', 'state', 'name')
    		else: columns = ('id', 'state', 'name', 'owner', 'priority', 'code', 'start', 'slots', 'queue')
    		col_data = {}
    		for column in columns:
    			col_data[column] = {}
    			col_data[column]['length'] = max([len(str(jobs[j][column])) for j in jobs.keys()])
    			if args.header == True: col_data[column]['length'] = max(col_data[column]['length'], len(column))
    			col_data[column]['format_str'] = '{{{}:{}}}'.format(column, col_data[column]['length'])
    			col_data[column]['header_str'] = '{{:{}}}'.format(col_data[column]['length']).format(column)
    		sep_char = ' '
    		if args.header == True: print(sep_char.join([col_data[c]['header_str'] for c in columns]))
    		output_str = sep_char.join([col_data[c]['format_str'] for c in columns])
    		for job_id in sorted(jobs.keys()): print(output_str.format(**jobs[job_id]))

# If run as main, run main():
if __name__ == '__main__': main()
