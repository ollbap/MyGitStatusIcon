#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun May 20

@author: ollbap
"""

import gobject
import gtk
import os
from MyUtil import myPrint
from MyGitUtil import gitCheckDirtyStateRecursive
from MyGitUtil import DirtyState
from MyConfig import readConfig
import threading
import time

#http://www.pygtk.org/pygtk2reference/class-gtkstatusicon.html

CONFIG = readConfig()

AUTO_CHECK_MODE = CONFIG.getboolean('InitialState', 'auto_check')
AUTO_CHECK_FREQUENCY_SECONDS = 60 * CONFIG.getint('InitialState', 'auto_check_frequency_minutes')
ONLINE_CHECK_MODE = CONFIG.getboolean('InitialState', 'online_check')


GIT_ONLINE_ROOT_PATHS=CONFIG.get('CheckPaths','online_root_paths')
GIT_OFFLINE_ROOT_PATHS=CONFIG.get('CheckPaths','offline_root_paths')

GTK_ICON = None

ICON_CLEAN="icons/f-check_256.svg"
ICON_ERROR="icons/f-cross_256.svg"
ICON_WORKING="icons/f-server_128.svg"
ICON_UPLOAD="icons/f-top_256.svg"
ICON_DOWNLOAD="icons/f-bottom_256.svg"

ICON_OPTIONS={
        DirtyState.CLEAN:         ICON_CLEAN,
        DirtyState.LOCAL_DIRTY:   ICON_UPLOAD,
        DirtyState.REMOTE_AHEAD:  ICON_UPLOAD,
        DirtyState.REMOTE_BEHIND: ICON_DOWNLOAD,
        DirtyState.ERROR:         ICON_ERROR,
        }

def check_now (val):
    global GIT_ONLINE_ROOT_PATHS
    global GIT_OFFLINE_ROOT_PATHS
    
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

def updateIconState(state):
    global GTK_ICON
    myPrint("    Update state "+str(state))
    GTK_ICON.set_tooltip("State: "+str(state))
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

def make_menu(event_button, event_time, data=None):
    menu = gtk.Menu()
    
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

    check_item = gtk.MenuItem("Check")
    menu.append(check_item)
    check_item.connect_object("activate", check_now, ())
    check_item.show()
    
    kill_item = gtk.MenuItem("Quit")
    menu.append(kill_item)
    kill_item.connect_object("activate", gtk.main_quit, ())
    kill_item.show()
    
    menu.popup(None, None, None, event_button, event_time)

def on_right_click(data, event_button, event_time):
    make_menu(event_button, event_time)

def on_left_click(event):
    check_now(())
    
def autoCheckTimer():
    global AUTO_CHECK_FREQUENCY_SECONDS
    time.sleep(1)
    while True:
        check_now(())
        time.sleep(AUTO_CHECK_FREQUENCY_SECONDS)

def initStatusIcon():
    global ICON_WORKING
    global GTK_ICON
    gobject.threads_init()
    os.chdir(os.path.dirname(__file__))
    #GTK_ICON = gtk.status_icon_new_from_file(ICON_WORKING)
    GTK_ICON = gtk.StatusIcon()
    GTK_ICON.connect('popup-menu', on_right_click)
    GTK_ICON.connect('activate', on_left_click)
    
    t = threading.Thread(target=autoCheckTimer)
    t.start()
    
if __name__ == '__main__':
    initStatusIcon()
    #check_now(())
    gtk.main()