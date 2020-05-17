#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 20

@author: ollbap
"""

from pystray import MenuItem as item
import pystray
from PIL import Image

import traceback
import os
from MyUtil import myPrint
from MyGitUtil import gitCheckDirtyStateRecursive
from MyGitUtil import DirtyState
from MyConfig import readConfig
from Gui import myGuiMessage
import threading
import time
from Gui import showDirtyDirectories

# http://www.pygtk.org/pygtk2reference/class-gtkstatusicon.html

CONFIG = readConfig()

DEBUG_MODE = False

AUTO_CHECK_TIMER_THREAD = None
LAST_CHECK_RESULT = None
LAST_CHECK_STATUS = None

AUTO_CHECK_MODE = CONFIG.getboolean('InitialState', 'auto_check')
AUTO_CHECK_FREQUENCY_SECONDS = 60 * CONFIG.getint('InitialState', 'auto_check_frequency_minutes')
FORCE_AUTO_SHOW_CHECK_DIALOG_TIMES = CONFIG.getint('InitialState', 'force_auto_show_check_dialog_times')

if DEBUG_MODE:
    AUTO_CHECK_FREQUENCY_SECONDS = AUTO_CHECK_FREQUENCY_SECONDS / 60

ONLINE_CHECK_MODE = CONFIG.getboolean('InitialState', 'online_check')

GIT_ONLINE_ROOT_PATHS = CONFIG.get('CheckPaths', 'online_root_paths').split(',')
GIT_OFFLINE_ROOT_PATHS = CONFIG.get('CheckPaths', 'offline_root_paths').split(',')

ICON = None

ICON_CLEAN = "icons/f-check_256.png"
ICON_ERROR = "icons/f-cross_256.png"
ICON_WORKING = "icons/f-server_128.png"
ICON_UPLOAD = "icons/f-top_256.png"
ICON_DOWNLOAD = "icons/f-bottom_256.png"
ICON_LOCAL_CHANGES = "icons/f-my_left_right_256.png"

ICON_OPTIONS = {
    DirtyState.CLEAN: ICON_CLEAN,
    DirtyState.LOCAL_DIRTY: ICON_LOCAL_CHANGES,
    DirtyState.REMOTE_AHEAD: ICON_UPLOAD,
    DirtyState.REMOTE_BEHIND: ICON_DOWNLOAD,
    DirtyState.ERROR: ICON_ERROR,
}


def check_from_gui(val):
    check_in_background()


def check_in_background():
    t = threading.Thread(target=check_now)
    t.daemon = True
    t.start()


def check_now():
    try:
        global GIT_ONLINE_ROOT_PATHS
        global GIT_OFFLINE_ROOT_PATHS
        global LAST_CHECK_RESULT
        global LAST_CHECK_STATUS

        updateIconAsWorking()
        myPrint("Checking now")

        m1 = gitCheckDirtyStateRecursive(GIT_ONLINE_ROOT_PATHS, ONLINE_CHECK_MODE)
        m2 = gitCheckDirtyStateRecursive(GIT_OFFLINE_ROOT_PATHS, ONLINE_CHECK_MODE)
        states = {**m1, **m2}

        maxState = DirtyState.CLEAN
        for path, state in states.items():
            if state != DirtyState.CLEAN:
                myPrint("%15s | %s" % (state.name, path))
            if state.value > maxState.value:
                maxState = state

        updateIconState(maxState)
        LAST_CHECK_RESULT = states
        LAST_CHECK_STATUS = maxState
    except:
        traceback.print_exc()
        myGuiMessage("Check failed", traceback.format_exc())


def showLastDirtyDirectories():
    showDirtyDirectories(LAST_CHECK_RESULT)
    check_now()


def showLastDirtyDirectories_FromGuiBackground(ignored):
    global LAST_CHECK_RESULT
    t = threading.Thread(target=showLastDirtyDirectories)
    t.daemon = True
    t.start()


def updateIconState(state):
    global ICON
    myPrint("    Update state " + str(state))
    ICON.icon = Image.open(ICON_OPTIONS[state])


def updateIconAsWorking():
    global ICON
    myPrint("    Update state Working")
    ICON.icon = Image.open(ICON_WORKING)


def change_AUTO_CHECK_MODE(auto_item):
    global AUTO_CHECK_MODE
    AUTO_CHECK_MODE = auto_item.active
    myPrint("Auto mode:" + str(AUTO_CHECK_MODE))


def change_online_mode(item):
    global ONLINE_CHECK_MODE
    ONLINE_CHECK_MODE = item.active
    myPrint("Online mode:" + str(ONLINE_CHECK_MODE))


def quit_callback(ignored):
    global AUTO_CHECK_TIMER_THREAD
    myPrint("Quitting")
    # TODO QUIT


def showUpdatesOrCheck(event):
    global LAST_CHECK_STATUS
    if LAST_CHECK_STATUS == DirtyState.CLEAN:
        check_from_gui(())
    else:
        showLastDirtyDirectories_FromGuiBackground(())


def autoCheckTimer():
    global AUTO_CHECK_FREQUENCY_SECONDS
    global AUTO_CHECK_MODE

    time.sleep(10)
    dirtyTimesToForce = 0
    while True:
        if AUTO_CHECK_MODE:
            check_now()
            if LAST_CHECK_STATUS != DirtyState.CLEAN:
                dirtyTimesToForce += 1
            else:
                dirtyTimesToForce = 0

            if dirtyTimesToForce >= FORCE_AUTO_SHOW_CHECK_DIALOG_TIMES:
                showLastDirtyDirectories_FromGuiBackground(())
                dirtyTimesToForce = 0
        time.sleep(AUTO_CHECK_FREQUENCY_SECONDS)


def initStatusIcon():
    global ICON_WORKING
    global ICON
    global AUTO_CHECK_TIMER_THREAD

    os.chdir(os.path.dirname(__file__))

    AUTO_CHECK_TIMER_THREAD = threading.Thread(target=autoCheckTimer)
    # So application does not hang
    AUTO_CHECK_TIMER_THREAD.daemon = True
    AUTO_CHECK_TIMER_THREAD.start()

    menu = (
        item("Show updates", showUpdatesOrCheck),
        item("Check", check_from_gui),
        item("Quit", quit_callback)
    )

    firstIconImage = Image.open(ICON_WORKING)

    ICON = pystray.Icon("Icon Title", firstIconImage, "title", menu)
    ICON.run()


if __name__ == '__main__':
    initStatusIcon()
