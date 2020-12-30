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
from imp import reload

############
# SETTINGS #
############
dirname, filename = os.path.split(os.path.abspath(__file__))

# how long to sleep between two checks, default 2 secs
CHECK_INTERVAL = 2  # unit, seconds

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
    cmd = "last -awdFi"
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


def in_white_list(loginStr):
    if LOGIN_WHITE_LIST == []:
        return False
    else:
        loginList = loginStr.split()
        user = loginList[0]
        ip = loginList[-1]
        loginDict = {"user": user, "ip": ip}
        loginAllAddr = {"user": user, "ip": "*"}
        loginAllUser = {"user": "*", "ip": ip}
    if loginDict in LOGIN_WHITE_LIST:  # {"user": "foo1", "ip": "123.123.123.123"}
        return True
    if loginAllAddr in LOGIN_WHITE_LIST:  # {"user": "foo2", "ip": "*"}
        return True
    if loginAllUser in LOGIN_WHITE_LIST:  # {"user": "*", "ip": "124.124.124.124"}
        return True
    return False
    

def untrust_login():
    lastNow = get_last()
    time.sleep(2)
    lastLater = get_last()
    if lastLater != lastNow:
        (newLast, oldestLast) = return_not_matches(lastNow, lastLater)
        newLogin = []
        for line in newLast:
            if not re.match("reboot   system boot", line) \
               and re.search("still logged in", line):  # if you want to alert logout, remove this line
            # remove lines of reboot like below
            # reboot   system boot  Wed Dec 30 22:47:10 2020
            # and ignore closed user after log out
                newLogin.append(line)
        untrustLogin = []
        if newLogin != []:
            print("New login found")
            for loginStr in newLogin:
                inWhiteList = in_white_list(loginStr)
                if inWhiteList != True:
                    untrustLogin.append(loginStr)
            if untrustLogin != []:
                return untrustLogin
            else:
                return None
        else:
            #print("No new login, sleep 2 secs")
            return None
    else:
        return None
        #print("No new login, sleep 2 secs")


if __name__ == '__main__':
    while True:
        reload(local_settings)
        try:
            LOGIN_WHITE_LIST = local_settings.LOGIN_WHITE_LIST
        except:
            LOGIN_WHITE_LIST = []
        untrustLogin = untrust_login()
        if untrustLogin != None:
            summary = str(untrustLogin)
            title = "Untrust login found"
            # TODO add send mail
            # send_mail(title, message = summary)
            trigger_incident(summary)
