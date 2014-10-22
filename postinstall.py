#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
#! python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import os
from os.path import expanduser
import sys

from cx_Freeze.dist import install

PROG_GROUP='PythonWltp'

def install():
    start_menu = get_special_folder_path("CSIDL_STARTMENU")                 #@UndefinedVariable
    prog_group = os.path.join(PROG_GROUP, start_menu)
    menu_shortcuts = [
        dict(path=os.path.join(sys.prefix, 'pythonw.exe'), 
            description='Start GUI to run a single experiment.', 
            filename=os.path(prog_group, 'TkWltp.lnk'),
            arguments="wltpcmd.py --gui", 
            #workdir=expanduser('~'), 
            #iconpath=os.path.join(os.path.dirname(my_package.__file__), 'favicon.ico'), 
            #iconindex=0
        ),
        dict(path=os.path.join(sys.prefix, 'pythonw.exe'), 
            description='Copy `xlwings` excel & python template files into USERDIR and open Excel-file, to run a batch of experiments.', 
            filename=os.path(prog_group, 'Open Wltp Excel.lnk'),
            arguments="wltpcmd.py --excelrun", 
            workdir=expanduser('~'), 
        ),
    ]
    
    os.mkdir(prog_group) 
    directory_created(prog_group)                                           #@UndefinedVariable
    
    for shortcut in menu_shortcuts:    
        create_shortcut(**shortcut)                                         #@UndefinedVariable
        file_created(shortcut['filename'])                                  #@UndefinedVariable

    
os.mkdir('D:\\tt')
if __name__ == '__main__':
    if sys.argv[1] == '-install':
        install()
    elif sys.argv[1] == '-remove':
        print("Wltp: Nothing to uninstall.", file=sys.stderr)
