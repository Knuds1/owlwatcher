#!python
# coding: utf-8

import os
import sys
import time
import datetime
import json
import random
import shutil
import arrow
import ctypes
from shlex import quote
from sys import platform
from os.path import expanduser
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def main():
    set_title('Overwatch League Watcher')
    clear_screen()

    # Setup webdriver for proper platform
    options = webdriver.ChromeOptions()
    if platform.startswith('linux'):
        options.add_argument('user-data-dir=' + expanduser('~') + '/.config/google-chrome')
        driverpath = resource_path('chromedriver')
    elif platform == 'darwin':
        options.add_argument('user-data-dir=' + expanduser('~') + '/Library/Application Support/Google/Chrome')
        driverpath = resource_path('chromedriver_osx')
    elif platform == 'win32':
        options.add_argument('user-data-dir=' + expanduser('~') + '\\AppData\\Local\\Google\\Chrome\\User Data')
        driverpath = resource_path('chromedriver.exe')
    else:
        modal('Unsupported platform: {}'.format(platform))
        sys.exit(-1)

    options.add_argument('log-level=3')
    options.add_argument('mute-audio')
    options.add_argument('disable-background-mode')
    options.add_argument('disable-plugins')
    options.add_argument('app-auto-launched')
    options.add_argument('fast-start')

    while(True):
        # Get daily OWL schedule
        days = get_daily_start_end_times()

        # Process days in order
        for day in days:
            random_open_time = random.randint(-900, 300)
            random_close_time = random.randint(-300, 900)

            # Calculate open and close times for the day's stream
            open_time = day[0]
            close_time = day[1]

            # Skip day if it is already over
            if close_time <= datetime.datetime.now():
                continue

            # Check if too early to open stream
            if open_time > datetime.datetime.now():
                # Calculate seconds until when to open stream
                wait_time = (open_time - datetime.datetime.now()).total_seconds()
                sleep_time = wait_time + random_open_time

                # Sleep until time to open stream
                starts_in = arrow.utcnow().shift(seconds=wait_time)

                while sleep_time > 0:
                    set_title('Next Overwatch League stream {} {}{}'.format(future_past('starts', 'started', starts_in), starts_in.humanize(), future_past('...', '', starts_in)))
                    modal('Next stream {} {}{}'.format(future_past('starts', 'started', starts_in), starts_in.humanize(), future_past('...', '.\n\nStream will open automatically...', starts_in)))
                    if sleep_time >= 60:
                        time.sleep(60)
                    else:
                        time.sleep(sleep_time % 60)
                    sleep_time -= 60

            # Open the stream

            while True:
                try:
                    driver = webdriver.Chrome(driverpath, chrome_options=options)
                    modal('Opening Overwatch League stream...')
                    break
                except Exception as e:
                    if 'user data directory is already in use' in str(e):
                        modal('Google Chrome is already running, please close Chrome to continue...'.format(str(e)))
                    else:
                        modal(str(e))
                    time.sleep(3000)

            driver.get('https://twitch.tv/overwatchleague')

            try:
                # Get video element from page
                elem = driver.find_element_by_xpath('//video')
                # Send PAGE_DOWN key to mute stream
                elem.send_keys(Keys.PAGE_DOWN)
            except:
                pass
            
            # Calculate seconds until when to close stream
            start_time = (open_time - datetime.datetime.now()).total_seconds()
            end_time = (close_time - datetime.datetime.now()).total_seconds()
            sleep_time = end_time + random_close_time

            # Sleep until time to close stream
            starts_in = arrow.utcnow().shift(seconds=start_time)
            ends_in = arrow.utcnow().shift(seconds=end_time)
            while sleep_time > 0:
                set_title('The Overwatch League stream {} {}{}'.format(future_past('starts', 'started', starts_in), starts_in.humanize(), future_past('...', '', starts_in)))
                modal('The stream {} {}, {} {}.\n\n{}'.format(
                    future_past('starts', 'started', starts_in),
                    starts_in.humanize(),
                    future_past('ends', 'ended', ends_in),
                    ends_in.humanize(),
                    future_past('Enjoy!', 'The window will close automatically...', ends_in))
                )
                if sleep_time >= 60:
                    time.sleep(60)
                else:
                    time.sleep(sleep_time % 60)
                sleep_time -= 60

            # Close the stream
            modal('Closing Overwatch League stream...')
            driver.close()

def modal(string):
    size = shutil.get_terminal_size()
    lines = string.strip('\n').split('\n')
    pre = '\n' * (size.lines // 2 - len(lines) // 2)
    clear_screen()
    print(pre + '\n'.join([line.center(size.columns - 1) for line in lines]), end='\n', flush=True)

def clear_screen():
    if platform == 'win32':
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        sys.stdout.write("\033[H\033[J")

def set_title(title):
    if platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        sys.stdout.write("\x1b]2;{}\x07".format(title))

def future_past(future, past, time):
    return future if time > arrow.utcnow() else past

# Returns a list of datetime pairs to represent the start
# and end times for OWL matches for each day
def get_daily_start_end_times():
    # Fetch the latest schedule from the Overwatch League API
    request = urlopen('https://api.overwatchleague.com/schedule')
    schedule = json.loads(request.read())

    day = None
    days = []

    # Loop through each stage
    for stage in schedule['data']['stages']:
        # Loop through each match
        for match in stage['matches']:
            # Only process non-completed matches
            if match['state'] != 'PENDING':
                continue

            # Get match start and end times
            start_date = datetime.datetime.fromtimestamp(match['startDateTS']/1000) - datetime.timedelta(hours=1)
            end_date = datetime.datetime.fromtimestamp(match['endDateTS']/1000) - datetime.timedelta(hours=1)
            
            # Update daily start and end times
            if not day:
                day = [ start_date, end_date ]
            else:
                # Calucate time difference in hours between match start time 
                # and existing day start time
                hours = (start_date - day[0]).total_seconds() // 3600

                # Consider match as starting on the next day if it starts at least
                # 12 hours after the start of the previous day.
                if hours >= 12:
                    # Store day times and start new day
                    days.append(day)
                    day = [ start_date, end_date ]
                else:
                    # Update end time for the day
                    day[1] = end_date

    # Return daily info
    return days

def resource_path(relative_path):
    '''Get absolute path to resource, works for dev and for PyInstaller'''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)
                
if __name__ == '__main__':
    main()