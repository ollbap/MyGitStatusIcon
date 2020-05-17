#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun May 21 10:42:36 2017

@author: ollbap
"""

import configparser
import os
import sys
import json
from MyUtil import myPrint


def configTest():
    cpath = _getConfigurationFilePath()
    config = _readConfig(cpath)
    printConfig(config)
    config.getboolean('InitialState', 'auto_check')
    p1 = config.get('CheckPaths', 'online_root_paths')
    p2 = config.get('CheckPaths', 'offline_root_paths')
    type(p1)
    type(p2)


def _getConfigurationFilePath():
    envirVar = os.environ.get("MY_GIT_STATUS_ICON_CONF_DIR")
    if envirVar is not None:
        base = envirVar
    else:
        base = os.path.expanduser("~/.config")

    return os.path.join(base, "myGitStatusIcon.init")


def _writeConfig(cpath):
    cfgfile = open(cpath, 'w')
    parser = configparser.ConfigParser()

    parser.add_section('InitialState')
    parser.set('InitialState', 'auto_check', "True")
    parser.set('InitialState', 'online_check', "True")
    parser.set('InitialState', 'auto_check_frequency_minutes', "10")
    parser.set('InitialState', 'force_auto_show_check_dialog_times', "6")

    parser.add_section('CheckPaths')
    parser.set('CheckPaths', 'online_root_paths', """ ["~/"]  """)
    parser.set('CheckPaths', 'offline_root_paths', """     []  """)

    parser.write(cfgfile)
    cfgfile.close()


def _readConfig(cpath):
    try:
        source = open(cpath, 'r')
    except IOError:
        sys.stderr.write('Configuration file not found in path "%s", new one going to be created\n' % (cpath))
        _writeConfig(cpath)
        source = open(cpath, 'r')

    parser = configparser.ConfigParser()
    parser.read_file(source)

    parser.set('CheckPaths', 'online_root_paths', json.loads(parser.get('CheckPaths', 'online_root_paths')))
    parser.set('CheckPaths', 'offline_root_paths', json.loads(parser.get('CheckPaths', 'offline_root_paths')))

    return parser


def printConfig(config):
    for section in config.sections():
        myPrint(section)
        for name, value in config.items(section):
            myPrint('  %s = %r' % (name, value))


def readConfig():
    cpath = _getConfigurationFilePath()
    return _readConfig(cpath)


if __name__ == "__main__":
    configTest()
