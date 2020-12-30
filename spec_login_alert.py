#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
    The script is used to check the last login user. If not in local_settings.py LOGIN_WHITE_LIST,
send alert to pagerduty and email.
"""

import os
import re
import subprocess,shlex
import local_settings
import time
from pagerduty import trigger_incident

############
# SETTINGS #
############
dirname, filename = os.path.split(os.path.abspath(__file__))

# how long to sleep between two checks, default 2 secs
CHECK_INTERVAL = 2  # unit, seconds

PAGERDUTY_API_ACCESS_KEY = local_settings.PAGERDUTY_API_ACCESS_KEY
PAGERDUTY_ROUTING_KEY = local_settings.PAGERDUTY_ROUTING_KEY

try:
    LOGIN_WHITE_LIST = local_settings.LOGIN_WHITE_LIST
except:
    LOGIN_WHITE_LIST = []

def return_not_matches(a, b):
    a = set(a)
    b = set(b)
    return [list(b - a), list(a - b)]
"""
a=[ 1,2,3,4,5 ]
b=[ 1,2,3,6 ]
return_not_matches(a,b)
[[6], [4, 5]]
"""


def get_last():
    # use linux command : last -a
    # to get the latest login user
    cmd = "last -adFi"
    cmd = shlex.split(cmd)
    try:
        lastResult = subprocess.check_output(cmd)
        code = 0
        lastResult = lastResult.decode('utf-8')  # check_output reuslt is a byte style
        # print(lastResult)
        return lastResult.split("\n")
    except subprocess.CalledProcessError as e:
        lastResult = e.output       # Output generated before error
        lastResult = lastResult.decode('utf-8')  # check_output reuslt is a byte style
        code      = e.returncode   # Return code
        print("[ERROR] run followed shell command error") 
        print(' '.join(cmd))
        print(lastResult)
        exit()
        return False 


def new_login():
    lastNow = get_last()
    time.sleep(2)
    lastLater = get_last()
    if lastLater != lastNow:
        (newLast, oldestLast) = return_not_matches(lastNow, lastLater)
        newLogin = []
        for line in newLast:
            if not re.match("reboot   system boot", line):
            # remove lines of reboot like below
            # reboot   system boot  Wed Dec 30 22:47:10 2020
                newLogin.append(line)
        if newLogin != []:
            print("New login found")
            return newLogin
        else:
            #print("No new login, sleep 2 secs")
            return None
    else:
        return None
        #print("No new login, sleep 2 secs")


if __name__ == '__main__':
    while True:
        newLogin = new_login()
        if newLogin != None:
            summary = str(newLogin)
            title = "New login found"
            # TODO add send mail
            # send_mail(title, message = summary)
            trigger_incident(summary)
