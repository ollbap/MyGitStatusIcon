#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 27 18:17:24 2017

@author: ollbap
"""

from tkinter import Label
from tkinter import LEFT
from MyGitUtil import gitPull
from MyGitUtil import gitPush
import traceback

import tkinter
from subprocess import call

from MyGitUtil import DirtyState


def handleGitDir(path, status):
    try:
        print("Handling: "+str(path)+" "+str(status))
        if status == DirtyState.REMOTE_AHEAD:
            gitPush(path)
            return
        
        if status == DirtyState.REMOTE_BEHIND:
            gitPull(path)
            return
            
        call(["xterm", "-e", """cd '"""+str(path)+"""'; bash"""])    
        print("Done")
    except:
        traceback.print_exc()
        myGuiMessage("Operation failed", traceback.format_exc())


def myGuiMessage(title, message) :
    messageWindow = tkinter.Tk()
    messageWindow.wm_title(title)
    Label(messageWindow, text=message, justify=LEFT).pack()
    messageWindow.mainloop()


def showDirtyDirectories(dirDictionary):
    rootWindow = tkinter.Tk()
    rootWindow.wm_title("Git dirty directories")
    # title = Label(rootWindow, text="Git Directories")
    # title.pack()
    
    rowIndex = 0
    for path, status in dirDictionary.iteritems():
        if status != DirtyState.CLEAN:
            button = tkinter.Button(rootWindow,
                                    width=15,
                                    text=status.name,
                                    command=lambda path=path, status=status: handleGitDir(path, status))
            button.grid(row=rowIndex, column=0)
            Label(text=path, justify=LEFT, anchor="e").grid(row=rowIndex,column=1, sticky="W")
            rowIndex += 1

    rootWindow.mainloop()


def guiTest():
    dirDictionary = {"/home/test/aaa/ccc": DirtyState.LOCAL_DIRTY,
                     "/home/test/ddd/eee": DirtyState.LOCAL_DIRTY,
                     "/home/test/ddd/dddasdasd/asdds": DirtyState.REMOTE_AHEAD,
                     "/home/test/ddd/cc": DirtyState.REMOTE_BEHIND,
                     "/home/test/": DirtyState.CLEAN}

    showDirtyDirectories(dirDictionary)


if __name__ == "__main__":
    guiTest()