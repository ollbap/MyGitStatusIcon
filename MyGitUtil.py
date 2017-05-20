from git import Repo
#https://gitpython.readthedocs.io/en/stable/reference.html#module-git.repo.base
from enum import Enum

class DirtyState(Enum):
    CLEAN = 1
    LOCAL_DIRTY = 2
    REMOTE_AHEAD = 3
    REMOTE_BEHIND = 4

def test():
    """ Test function """
    git_directory="/home/ollbap/test_dir"
    repo = Repo(git_directory)
    assert not repo.bare
    
    #Untracked
    dirty = repo.is_dirty() or repo.untracked_files.__len__() > 0 
    print(dirty)
    
    b1 = repo.branches[0]
    b1.tracking_branch()
    commits_behind = repo.iter_commits('master..origin/master')
    commits_ahead = repo.iter_commits('origin/master..master')
    
    sum(1 for c in commits_behind)
    sum(1 for c in commits_ahead)

    gitCheckDirtyState("/home/ollbap/test_dir", True)
    gitCheckDirtyState("/home/ollbap/test_dir", False)
    
def gitCheckDirtyState(git_directory, online):
    """ Returns a boolean to indicate if the git repository in the path is 
    dirty. 
        path: a path root of the repository
        online: if also remotelly check if main branch is ahead or behind remote track. 
    """
    
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