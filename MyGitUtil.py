#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun May 20

@author: ollbap
"""

from git import Repo
#https://gitpython.readthedocs.io/en/stable/reference.html#module-git.repo.base
from enum import Enum

class DirtyState(Enum):
    CLEAN = 1
    LOCAL_DIRTY = 2
    REMOTE_AHEAD = 3
    REMOTE_BEHIND = 4
    ERROR = 5

def myGitTest():
    """ Test function """
    git_directory="/home/ollbap/test_dir"
    repo = Repo(git_directory)
    assert not repo.bare
    
    #Untracked
    dirty = repo.is_dirty() or repo.untracked_files.__len__() > 0 
    print("Dirty: %s" % dirty)
    
    b1 = repo.branches[0]
    b1.tracking_branch()
    commits_behind = repo.iter_commits('master..origin/master')
    commits_ahead = repo.iter_commits('origin/master..master')
    
    nb = sum(1 for c in commits_behind)
    na = sum(1 for c in commits_ahead)

    print("nb = %s na = %s", nb, na)

    s = gitCheckDirtyState("/home/ollbap/test_dir", True)
    print("s = %s", s)
    s = gitCheckDirtyState("/home/ollbap/test_dir", False)
    print("s = %s", s)
    
def gitCheckDirtyState(git_directory, online):
    """ Returns a boolean to indicate if the git repository in the path is 
    dirty. 
        path: a path root of the repository
        online: if also remotelly check if main branch is ahead or behind remote track. 
    """
    try:
        repo = Repo(git_directory)
    
        dirty = repo.is_dirty() or repo.untracked_files.__len__() > 0
        if dirty:
            return DirtyState.LOCAL_DIRTY
    
        if not online:
            return DirtyState.CLEAN
    
        ###
        #Online checks in branches
        ###
    
        if len(repo.branches) == 0:
            #This is a repository with no commits.
            return DirtyState.CLEAN
        
        if len(repo.branches) > 1:
            raise Exception("Repositories with multiple branches are not supported")
        
        b = repo.branches[0]
    
        if b.tracking_branch() == None:
            return DirtyState.CLEAN
            
        behindString = b.name + ".." + b.tracking_branch().name
        aheadString = b.tracking_branch().name + ".." + b.name
        
        commits_behind = repo.iter_commits(behindString)
        commits_ahead = repo.iter_commits(aheadString)
        
        count_behind = sum(1 for c in commits_behind)
        count_ahead = sum(1 for c in commits_ahead)
        
        if count_behind > 0:
            return DirtyState.REMOTE_BEHIND
        
        if count_ahead > 0:
                return DirtyState.REMOTE_AHEAD
        
        return DirtyState.CLEAN
    except:
        return DirtyState.ERROR

if __name__ == "__main__":
    myGitTest()