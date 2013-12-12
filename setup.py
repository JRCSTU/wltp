#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltcg.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


# wltcg's setup.py
from distutils.core import setup
import os

projname = 'wltcg'
mydir = os.path.dirname(__file__)


## Version-trick to have version-info in a single place,
## taken from: http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
##
def readversioninfo(fname):
    fglobals = {'__version_info__':('x', 'x', 'x')} # In case reading the version fails.
    exec(open(os.path.join(mydir, projname, fname)).read(), fglobals)  # To read __version_info__
    return fglobals['__version_info__']

# Trick to use README file as long_description.
#  It's nice, because now 1) we have a top level README file and
#  2) it's easier to type in the README file than to put a raw string in below ...
def readtxtfile(fname):
    return open(os.path.join(mydir, fname)).read()

setup(
    name = projname,
    packages = [projname],
    version = '.'.join(readversioninfo('_version.py')),
    description = "WLTC gear-shift calculator",
    author = "ankostis",
    author_email = "ankostis@gmail.com",
    url = "https://webgate.ec.europa.eu/CITnet/confluence/display/VECTO",
    download_url = "https://webgate.ec.europa.eu/CITnet/confluence/display/VECTO",
    license = "GNU Affero General Public License v3 or later (AGPLv3+)",
    keywords = ['wltc', 'cycles', 'emissions', 'simulation', 'vehicles', 'cars', 'nedc'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = readtxtfile('README.txt')
)
