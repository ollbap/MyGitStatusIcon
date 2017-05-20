## MyGitStatusIcon
This is a simple project that uses gitpython and gkt python api to create a status icon that notify the user when your local git working directories are dirty, ahead or behind.

The idea is to have something in between git and dropbox. You get a cloud storage using git as a low level storage with concurrent version control and also have some automatic notifications to manually control your files and conflicts.

### How to execute
Run the `main.py` file in python using `./main.py` or any other manner. 

### Enviroments
Only tested for GTK linux on ARCH linux using python2.

### Configuration file
TODO

### Future work

 * Configuration files to specify what directories are checked, frequency,...
 * Popup notification.
 * Log with issues during automatic checks. Special icon for errors.
 * Support multiple branches
 * Operations GUI to run simple operations: pull, push, open command line, open git gui...
 * Commit GUI with add and revert options
 * Automatic pull and push according to some configurations somewhere

### Known bugs
 * Error with empty git directories, with no commits and untracked branch.
