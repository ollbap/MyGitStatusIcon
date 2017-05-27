#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 27 18:17:24 2017

@author: ollbap
"""

from Tkinter import Label
from Tkinter import X
from Tkinter import LEFT


import Tkinter
from subprocess import call

from MyGitUtil import DirtyState

def handleGitDir(path):
    print("Handling: "+str(path))
    call(["xterm", "-e", """cd '"""+str(path)+"""'; bash"""])    
    print("Done")
    
def showDirtyDirectories(dirDictionary):
    rootWindow = Tkinter.Tk()
    rootWindow.wm_title("Git dirty directories")
    #title = Label(rootWindow, text="Git Directories")
    #title.pack()
    
    rowIndex = 0
    for path, status in dirDictionary.iteritems():
        if status != DirtyState.CLEAN:
            button = Tkinter.Button(rootWindow, 
                                    width=15,
                                    text = status.name, 
                                    command=lambda path=path: handleGitDir(path))
            button.grid(row=rowIndex, column=0)
            Label(text=path, justify=LEFT, anchor="e").grid(row=rowIndex,column=1, sticky="W")
            rowIndex += 1

    rootWindow.mainloop()

def guiTest():
    dirDictionary = {}
    dirDictionary["/home/test/aaa/ccc"] = DirtyState.LOCAL_DIRTY
    dirDictionary["/home/test/ddd/eee"] = DirtyState.LOCAL_DIRTY
    dirDictionary["/home/test/ddd/dddasdasd/asdds"] = DirtyState.REMOTE_AHEAD
    dirDictionary["/home/test/ddd/cc"] = DirtyState.REMOTE_BEHIND
    dirDictionary["/home/test/"] = DirtyState.CLEAN
    showDirtyDirectories(dirDictionary)
    
if __name__ == "__main__":
    guiTest()