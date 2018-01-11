#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun May 20

@author: ollbap
"""

import traceback
import gobject
import gtk
import os
from MyUtil import myPrint
from MyGitUtil import gitCheckDirtyStateRecursive
from MyGitUtil import DirtyState
from MyConfig import readConfig
from Gui import myGuiMessage
import threading
import time
from Gui import showDirtyDirectories


#http://www.pygtk.org/pygtk2reference/class-gtkstatusicon.html

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


GIT_ONLINE_ROOT_PATHS=CONFIG.get('CheckPaths','online_root_paths')
GIT_OFFLINE_ROOT_PATHS=CONFIG.get('CheckPaths','offline_root_paths')

GTK_ICON = None

ICON_CLEAN="icons/f-check_256.svg"
ICON_ERROR="icons/f-cross_256.svg"
ICON_WORKING="icons/f-server_128.svg"
ICON_UPLOAD="icons/f-top_256.svg"
ICON_DOWNLOAD="icons/f-bottom_256.svg"
ICON_LOCAL_CHANGES="icons/f-my_left_right_256.svg"

ICON_OPTIONS={
        DirtyState.CLEAN:         ICON_CLEAN,
        DirtyState.LOCAL_DIRTY:   ICON_LOCAL_CHANGES,
        DirtyState.REMOTE_AHEAD:  ICON_UPLOAD,
        DirtyState.REMOTE_BEHIND: ICON_DOWNLOAD,
        DirtyState.ERROR:         ICON_ERROR,
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
        states = dict(m1.items() + m2.items())

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
    global GTK_ICON
    myPrint("    Update state "+str(state))
    GTK_ICON.set_tooltip("State: "+str(state.name))
    GTK_ICON.set_from_file(ICON_OPTIONS[state])

def updateIconAsWorking():
    global GTK_ICON
    myPrint("    Update state Working")
    GTK_ICON.set_tooltip("Working")
    GTK_ICON.set_from_file(ICON_WORKING)

def change_AUTO_CHECK_MODE (auto_item):
    global AUTO_CHECK_MODE
    AUTO_CHECK_MODE = auto_item.active
    myPrint("Auto mode:"+str(AUTO_CHECK_MODE))

def change_online_mode (item):
    global ONLINE_CHECK_MODE
    ONLINE_CHECK_MODE = item.active
    myPrint("Online mode:"+str(ONLINE_CHECK_MODE))

def quit_callback(ignored):
    global AUTO_CHECK_TIMER_THREAD
    global GTK_ICON

    GTK_ICON.set_visible(False)
    myPrint("Quitting")
    gtk.main_quit()

def make_menu(event_button, event_time, data=None):
    menu = gtk.Menu()

    show_dirty_item = gtk.MenuItem("Show Dirty")
    menu.append(show_dirty_item)
    show_dirty_item.connect_object("activate", showLastDirtyDirectories_FromGuiBackground, ())
    show_dirty_item.show()

    check_item = gtk.MenuItem("Check")
    menu.append(check_item)
    check_item.connect_object("activate", check_from_gui, ())
    check_item.show()

    auto_item = gtk.CheckMenuItem("Auto")
    auto_item.set_active(AUTO_CHECK_MODE)
    menu.append(auto_item)
    auto_item.connect_object("activate", change_AUTO_CHECK_MODE, (auto_item))
    auto_item.show()

    online_item = gtk.CheckMenuItem("Online")
    online_item.set_active(ONLINE_CHECK_MODE)
    menu.append(online_item)
    online_item.connect_object("activate", change_online_mode, (online_item))
    online_item.show()

    kill_item = gtk.MenuItem("Quit")
    menu.append(kill_item)
    kill_item.connect_object("activate", quit_callback, ())
    kill_item.show()

    menu.popup(None, None, None, event_button, event_time)

def on_right_click(data, event_button, event_time):
    make_menu(event_button, event_time)

def on_left_click(event):
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
    global GTK_ICON
    global AUTO_CHECK_TIMER_THREAD

    gobject.threads_init()
    os.chdir(os.path.dirname(__file__))

    GTK_ICON = gtk.status_icon_new_from_file(ICON_WORKING)
    GTK_ICON.connect('popup-menu', on_right_click)
    GTK_ICON.connect('activate', on_left_click)

    AUTO_CHECK_TIMER_THREAD = threading.Thread(target=autoCheckTimer)
    #So application does not hang
    AUTO_CHECK_TIMER_THREAD.daemon = True
    AUTO_CHECK_TIMER_THREAD.start()

if __name__ == '__main__':
    initStatusIcon()
    gtk.main()