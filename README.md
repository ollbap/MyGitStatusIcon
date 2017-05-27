
# MyGitStatusIcon
This is a simple project that uses gitpython and gkt python api to create a status icon that notify the user when your local git working directories are dirty, ahead or behind.

The idea is to have something midway between git and dropbox. You get a cloud storage using git as a low level storage with concurrent version control and also have some automatic notifications to remember to push and pull changes.

### Install dependencies
```
pip2 install gitpython
```

### How to execute
Run the `main.py` file in python using `./main.py` or any other manner.

### Enviroments
Only tested for GTK linux on ARCH linux using python2.

### Configuration file
A configuration file is created the first time that the program is executed at `~/.config/myGitStatusIcon.init`. This path can be changed
if the environment `MY_GIT_STATUS_ICON_CONF_DIR` is available.

The application needs to be restarted in order to load new configurations after edition. Variables are self-explanatory, note that arrays are provided as
json values, for example: `online_root_paths = ["~/Dropbox/data/", "~/scripts/"]`

Paths are expanded, meaning that `~` can be used to denote home path. A recursive search is executed from the paths to search for git repositories.

File example:
```
[InitialState]
auto_check = True
online_check = True
auto_check_frequency_minutes = 10
force_auto_show_check_dialog_times = 6

[CheckPaths]
online_root_paths = ["~/Dropbox/data/", "~/scripts/"]
offline_root_paths = []

```

### Future work
 * Support multiple branches
 * Log with issues during automatic checks. Special icon for errors.
 * Open git gui for local changes
 * Automatic commit, pull and push according to some configurations

### Known bugs and problems
 * Multi branch git repositories are not supported
