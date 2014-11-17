#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, unicode_literals

import argparse
import sys, os
import unittest


##############
#  Compatibility
#
try:
    assertRaisesRegex = unittest.TestCase.assertRaisesRegex
except:
    assertRaisesRegex = unittest.TestCase.assertRaisesRegexp

## Python-2 compatibility
#
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError  # @ReservedAssignment
else:
    FileNotFoundError = OSError  # @ReservedAssignment

def raise_ex_from(ex_class, chained_ex, *args, **kwds):
 from six import reraise


##############
#  Utilities
#
def str2bool(v):
    vv = v.lower()
    if (vv in ("yes", "true", "on")):
        return True
    if (vv in ("no", "false", "off")):
        return False
    try:
        return float(v)
    except:
        raise argparse.ArgumentTypeError('Invalid boolean(%s)!' % v)


def pairwise(t):
    '''From http://stackoverflow.com/questions/4628290/pairs-from-single-list'''
    it1 = iter(t)
    it2 = iter(t)
    try:
        next(it2)
    except:
        return []
    return zip(it1, it2)


## From http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
#
def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)




## From http://stackoverflow.com/a/4149190/548792
#
class Lazy(object):
    def __init__(self,func):
        self.func=func
    def __str__(self):
        return self.func()


def is_travis():
    return 'TRAVIS' in os.environ

def generate_filenames(filename):
    f, e = os.path.splitext(filename)
    yield filename
    i = 1
    while True:
        yield '%s%i%s' % (f, i, e)
        i += 1


def open_file_with_os(fpath):
    ## From http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python
    #     and http://www.dwheeler.com/essays/open-files-urls.html
    import subprocess
    try:
        os.startfile(fpath)
    except AttributeError:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', fpath))
        elif os.name == 'posix':
            subprocess.call(('xdg-open', fpath))
    return


###### WINDOWS ######
#####################

## From: http://stackoverflow.com/questions/2216173/how-to-get-path-of-start-menus-programs-directory  
# 
def win_shell():
    from win32com.client import Dispatch
    return Dispatch('WScript.Shell')

def win_folder(wshell, folder_name, folder_csidl=None):
    """
    
    :param wshell: win32com.client.Dispatch('WScript.Shell')
    :param str folder_name: ( StartMenu | MyDocuments | ... )
    :param str folder_csidl: see http://msdn.microsoft.com/en-us/library/windows/desktop/dd378457(v=vs.85).aspx
    """
    #from win32com.shell import shell, shellcon                          #@UnresolvedImport
    #folderid = operator.attrgetter(folder_csidl)(shellcon)
    #folder = shell.SHGetSpecialFolderPath(0, folderid)
    folder = wshell.SpecialFolders(folder_name)
    
    return folder

## See: http://stackoverflow.com/questions/17586599/python-create-shortcut-with-arguments
#    http://www.blog.pythonlibrary.org/2010/01/23/using-python-to-create-shortcuts/
#    but keep that for the future:
#        forgot chose: http://timgolden.me.uk/python/win32_how_do_i/create-a-shortcut.html
def win_create_shortcut(wshell, path, target_path, wdir=None, target_args=None, icon_path=None, desc=None):     
    """
    
    :param wshell: win32com.client.Dispatch('WScript.Shell')

    """
    
    is_url = path.lower().endswith('.url')
    shcut = wshell.CreateShortCut(path)
    try:
        shcut.Targetpath = target_path
        if icon_path:
            shcut.IconLocation = icon_path
        if desc:
            shcut.Description = desc
        if target_args:
            shcut.Arguments = target_args
        if wdir:
            shcut.WorkingDirectory = wdir
    finally:
        shcut.save()

def win_wshell():
    from win32com.client import Dispatch
    
    shell = Dispatch('WScript.Shell')

    return shell

