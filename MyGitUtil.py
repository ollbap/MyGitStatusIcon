#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 20

@author: ollbap
"""

import os
import fnmatch

from git import Repo
# https://gitpython.readthedocs.io/en/stable/reference.html#module-git.repo.base
from enum import Enum


class DirtyState(Enum):
    CLEAN = 1
    LOCAL_DIRTY = 2
    REMOTE_AHEAD = 3
    REMOTE_BEHIND = 4
    ERROR = 5


def myGitTest():
    """ Test function """
    git_directory = "~/test_dir/e"
    repo = Repo(git_directory)
    assert not repo.bare

    # Untracked
    dirty = repo.is_dirty() or repo.untracked_files.__len__() > 0
    print("Dirty: %s" % dirty)
    gitCheckDirtyStateRecursive(['~/test_dir'], True)
    gitCheckDirtyStateRecursive(['~/test_dir'], False)


def gitPush(git_directory):
    print("Pushing: " + git_directory)
    repo = Repo(os.path.expanduser(git_directory))

    if len(repo.remotes) > 1:
        raise Exception("Repositories with multiple remotes are not supported: " + git_directory)

    r1 = repo.remotes[0]
    r1.push()


def gitPull(git_directory):
    print("Pulling: " + git_directory)
    repo = Repo(os.path.expanduser(git_directory))

    if len(repo.remotes) > 1:
        raise Exception("Repositories with multiple remotes are not supported: " + git_directory)

    r1 = repo.remotes[0]
    r1.pull()


def gitCheckDirtyState(git_directory, online):
    """ Returns a boolean to indicate if the git repository in the path is 
    dirty. 
        path: a path root of the repository
        online: if also remotelly check if main branch is ahead or behind remote track. 
    """
    print(" - " + git_directory)
    repo = Repo(os.path.expanduser(git_directory))

    # First, check if it contains local changes, this is only tests for the current branch.
    # Is dirty checks changes from files that are in index and untracked_files checks files that are not currenly in index.
    # This is slow but I can't find a work around.
    dirty = repo.is_dirty() or len(repo.untracked_files) > 0
    if dirty:
        return DirtyState.LOCAL_DIRTY

    ###
    # Online checks in branches but only when online mode is enabled.
    ###
    if not online:
        return DirtyState.CLEAN

    if len(repo.branches) == 0:
        # This is a repository with no commits.
        return DirtyState.CLEAN

    # For each branch ckeck if it is ahead or behind
    # Return first not up to date status.
    foundStatus = DirtyState.CLEAN

    for branch in repo.branches:
        if branch.tracking_branch() is not None:
            behindString = branch.name + ".." + branch.tracking_branch().name
            aheadString = branch.tracking_branch().name + ".." + branch.name

            commits_behind = repo.iter_commits(behindString)
            commits_ahead = repo.iter_commits(aheadString)

            count_behind = sum(1 for c in commits_behind)
            count_ahead = sum(1 for c in commits_ahead)

            if count_behind > 0:
                print("    * " + branch.name + " -> REMOTE_BEHIND")
                if foundStatus == DirtyState.CLEAN:
                    foundStatus = DirtyState.REMOTE_BEHIND
            elif count_ahead > 0:
                print("    * " + branch.name + " -> REMOTE_AHEAD")
                if foundStatus == DirtyState.CLEAN:
                    foundStatus = DirtyState.REMOTE_AHEAD
            else:
                print("    * " + branch.name + " -> CLEAN")

    return foundStatus


def gitCheckDirtyStateRecursive(paths, online):
    resultMap = {}

    for path in paths:
        root_directory = os.path.expanduser(path)

        # Search each subdirectory at root_directory
        for root, dirnames, filenames in os.walk(root_directory):
            # Just process directories that match .git pattern
            for git_directory in fnmatch.filter(dirnames, '.git'):
                state = gitCheckDirtyState(root, online)
                # print("%s : %s" % (root, state))
                resultMap[root] = state

    return resultMap


if __name__ == "__main__":
    myGitTest()
