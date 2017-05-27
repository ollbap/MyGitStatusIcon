#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 27 18:17:24 2017

@author: ollbap
"""

from Tkinter import Label
import Tkinter
from subprocess import call

from MyGitUtil import DirtyState

def handleGitDir(path):
    print("Handling: "+str(path))
    call(["xterm", "-e", """cd '"""+str(path)+"""'; bash"""])    
    print("Done")
    
def showDirtyDirectories(dirDictionary):
    rootWindow = Tkinter.Tk()

    title = Label(rootWindow, text="Git Directories")
    title.pack()
    
    for path, status in dirDictionary.iteritems():
        if status != DirtyState.CLEAN:
            button = Tkinter.Button(rootWindow, 
                                    text=str(path)+":"+str(status), 
                                    command=lambda path=path: handleGitDir(path))
            button.pack()

    rootWindow.mainloop()

def guiTest():
    dirDictionary = {}
    dirDictionary["/home/test/aaa/ccc"] = DirtyState.LOCAL_DIRTY
    dirDictionary["/home/test/ddd/eee"] = DirtyState.LOCAL_DIRTY
    dirDictionary["/home/test/ddd/ddd"] = DirtyState.REMOTE_AHEAD
    dirDictionary["/home/test/ddd/cc"] = DirtyState.REMOTE_BEHIND
    dirDictionary["/home/test/ddd/jj"] = DirtyState.CLEAN
    showDirtyDirectories(dirDictionary)
    
if __name__ == "__main__":
    guiTest()