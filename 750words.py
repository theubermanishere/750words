#!/usr/bin/python3
# Program to read all files in the subdirectory Journal and report statistics

import datetime
import os
import re
import sys
import urllib3
from subprocess import call, run, check_output, PIPE, Popen


# Magic to ensure all things work as expected
basedir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(basedir)

# Black-hole for all STDOUT and STDERR
FNULL = open(os.devnull, 'w')

# Function to count the number of words written
def count_words():
    total_count = 0
    os.chdir('./Journal')
    for year in os.listdir():
        os.chdir(year)
        for month in os.listdir():
            os.chdir(month)
            for day in os.listdir():
                data = check_output(['wc','-w',day])
                total_count += int(data.decode("utf-8").strip().split(' ')[0])
            os.chdir('..')
        os.chdir('..')
    os.chdir('..')

    return "Total Count: " + str(total_count)

# Function to return path to today's entry
def get_todays_path():
    # Get today's date dateobject.
    today = datetime.date.today()
    # Get the year, month and day
    year, month, day = map(int, today.isoformat().split('-'))
    # Check if a entry exists
    filepath = (
            './Journal/' +
            str(year)+ '/' +
            str(month).rjust(2,'0') + '/' +
            str(day).rjust(2,'0'))
    return filepath


# Function to tell today's word-count.
def todays_count_words():
    global FNULL
    try:
        # Get path to today's entry
        filepath = get_todays_path()
        # Get word count
        data = check_output(['wc','-w', filepath], stderr=FNULL)
        total_count = int(data.decode("utf-8").strip().split(' ')[0])
        return "Today's Count: " + str(total_count)
    except:
        return "No Entry for Today"

# Function to print the last week progress
def last_week_stats():
    base = datetime.datetime.today()
    date_list_datetime = [base - datetime.timedelta(days=x) for x in range(0, 7)]
    date_list_isoformat = map(datetime.datetime.isoformat, date_list_datetime)
    date_list = list(map(lambda x: x[:10], date_list_isoformat))
    counts = []
    for date in date_list:
        year, month, day = date.split('-')
        try:
            filepath = (
                './Journal/' +
                str(year)+ '/' +
                str(month).rjust(2,'0') + '/' +
                str(day).rjust(2,'0'))
            data = check_output(['wc','-w', filepath], stderr=FNULL)
            wc = data.decode('utf-8').split(' ')[0]
            counts.append(int(wc.split(' ')[0]))
        except:
            counts.append(0)
    datafilename = 'week.dat'
    datafile = open(datafilename, 'w')
    for i in range(7):
        datafile.write(date_list[i].split('-')[2] + ' ' + str(counts[i]) + '\n')
    datafile.close()
    # GNU Plot
    gnuplot_commands = 'set terminal pngcairo font \'arial,10\' size 500,500; set boxwidth 0.75; set style fill solid; set term dumb; plot \'week.dat\' using 2:xtic(1) notitle with boxes'

    command_to_call = 'gnuplot -e "' + gnuplot_commands + '"'
    call(command_to_call, shell=True)
    os.remove(datafilename)

# Function to open a new file with today's date
def write_now():
    # Get path to today's entry
    filepath = get_todays_path()
    # Get Editor; Modify if you want some other editor
    editor = os.getenv('EDITOR')
    # Open File
    call([editor, filepath])

# Function to automatically git commit and upload
def save_entry():
    global FNULL
    # Get a funny commit message
    http = urllib3.PoolManager()
    commit_msg_page = http.request('GET', 'http://whatthecommit.com/').data.decode('utf-8')
    # Generate a reg exp for finding the text
    location = re.search('<div id="content">\n<p>', commit_msg_page)
    FNULL = open(os.devnull, 'w')
    start = location.end()
    end = commit_msg_page.find('\n',start)
    commit_msg = commit_msg_page[start:end]
    # Commit and push
    call(['git', 'add', '.'], stdout=FNULL)
    call(['git', 'commit', '-m', commit_msg], stdout=FNULL)
    call(['git', 'log'], stdout=FNULL)
    call(['git', 'push', 'origin', 'master'], stdout=FNULL)
    return 'Committed Successfully'

# Function to print log
def print_log():
    log_string = ['git', 'log', '--graph', '--full-history', '--all', '--color', '--date=short', '--pretty=format:"%Cred%x09%h %Creset%ad%Cblue%d %Creset %s %C(bold)(%an)%Creset"']
    output = check_output(log_string).decode('utf-8')

    return output

# check if the seconds argument is stats
if len(sys.argv) > 1 and (sys.argv[1] == 'stats' or sys.argv[1] == 's'):
    print(todays_count_words())
    print(count_words())
    last_week_stats()
elif len(sys.argv) > 1 and (sys.argv[1] == 'commit' or sys.argv[1] == 'c'):
    print(save_entry())
elif len(sys.argv) > 1 and (sys.argv[1] == 'log' or sys.argv[1] == 'l'):
    print(print_log())
else:
    print(write_now())

