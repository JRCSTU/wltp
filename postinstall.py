#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, unicode_literals

import logging
from os.path import expanduser
import sys, os
import tempfile


def _init_logging(loglevel):
    logging.basicConfig(level=loglevel)
    rlog = logging.getLogger()
    rlog.setLevel(level=loglevel)
    h = os.path.join(tempfile.gettempdir(), 'wltp.log')
    h = logging.FileHandler(h)
    rlog.addHandler(h)

_init_logging(logging.INFO)
log = logging.getLogger(__name__)


PROG_GROUP='PythonWltp'
SCRIPT_PATH = os.path.join(sys.prefix, "Scripts", "wltpcmd")

def install():
    start_menu = get_special_folder_path("CSIDL_STARTMENU")                 #@UndefinedVariable
    log.info('Writing to %s', start_menu)
    prog_group = os.path.join(start_menu, PROG_GROUP)
    menu_shortcuts = [
        dict(path=SCRIPT_PATH, 
            description='Start GUI to run a single experiment.', 
            filename=os.path.join(prog_group, 'TkWltp.lnk'),
            arguments="--gui", 
            #workdir=expanduser('~'), 
            #iconpath=os.path.join(os.path.dirname(my_package.__file__), 'favicon.ico'), 
            #iconindex=0
        ),
        dict(path=SCRIPT_PATH, 
            description='Copy `xlwings` excel & python template files into USERDIR and open Excel-file, to run a batch of experiments.', 
            filename=os.path.join(prog_group, 'New Wltp Excel.lnk'),
            arguments="--excelrun", 
            workdir=expanduser('~'), 
        ),
    ]
    
    try:
        os.mkdir(prog_group) 
        log.info('Created program-group(%s).', prog_group)
        directory_created(prog_group)                                       #@UndefinedVariable
    except:
        pass    ## Probably already exists.
    
    for shortcut in menu_shortcuts:    
        log.info('Creating shortcut: %s...', shortcut)
        create_shortcut(**shortcut)                                         #@UndefinedVariable
        file_created(shortcut['filename'])                                  #@UndefinedVariable

    
if __name__ == '__main__':
    op = sys.argv[1]
    log.info('Invoked with operation(%s).', op)
    if op == '-install':
        install()
    elif op == '-remove':
        print("Wltp: Nothing to uninstall.", file=sys.stderr)

