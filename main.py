#!/usr/bin/python2
import gobject
import gtk
import os
import sys
from MyGitUtil import gitCheckDirtyState
from MyGitUtil import DirtyState

#http://www.pygtk.org/pygtk2reference/class-gtkstatusicon.html

last_changed_time = 0
autoMode = True
onlineMode = True
git_directory="/home/ollbap/test_dir"

GTK_ICON = None

ICON_CLEAN="icons/f-check_256.svg"
ICON_NOT_CLEAN="icons/f-cross_256.svg"
ICON_WORKING="icons/f-server_128.svg"

ICON_OPTIONS={
        DirtyState.CLEAN:         ICON_CLEAN,
        DirtyState.LOCAL_DIRTY:   ICON_NOT_CLEAN,
        DirtyState.REMOTE_AHEAD:  ICON_NOT_CLEAN,
        DirtyState.REMOTE_BEHIND: ICON_NOT_CLEAN,
        }

def myPrint(s):
    print(s)
    sys.stdout.flush()

def check_now (val):
    myPrint("Check now")
    state = gitCheckDirtyState(git_directory, onlineMode)
    updateIconState(state)

def updateIconState(state):
    global GTK_ICON
    myPrint("Update state "+str(state))
    GTK_ICON.set_tooltip("State: "+str(state))
    GTK_ICON.set_from_file(ICON_OPTIONS[state])

def updateIconAsWorking():
    global GTK_ICON
    myPrint("Update state Working")
    GTK_ICON.set_tooltip("Working")
    GTK_ICON.set_from_file(ICON_WORKING)

def change_auto_mode (auto_item):
    global autoMode
    autoMode = auto_item.active
    myPrint("Auto mode:"+str(autoMode))

def change_online_mode (item):
    global onlineMode
    onlineMode = item.active
    myPrint("Online mode:"+str(onlineMode))

def make_menu(event_button, event_time, data=None):
    menu = gtk.Menu()
    
    auto_item = gtk.CheckMenuItem("Auto")
    auto_item.set_active(autoMode)
    menu.append(auto_item)
    auto_item.connect_object("activate", change_auto_mode, (auto_item))
    auto_item.show()

    online_item = gtk.CheckMenuItem("Online")
    online_item.set_active(onlineMode)
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

def initStatusIcon():
    global ICON_WORKING
    global GTK_ICON
    gobject.threads_init()
    os.chdir(os.path.dirname(__file__))
    #GTK_ICON = gtk.status_icon_new_from_file(ICON_WORKING)
    GTK_ICON = gtk.StatusIcon()
    updateIconAsWorking()
    GTK_ICON.connect('popup-menu', on_right_click)
    GTK_ICON.connect('activate', on_left_click)
    
if __name__ == '__main__':
    initStatusIcon()
    check_now(())
    gtk.main()