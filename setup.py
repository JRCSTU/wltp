#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

''''A calculator of gear-shifts of light-duty-vehicles (cars) for the WLTC testing-cycle.

Overview:
=========

WLTCG accepts as input the car-specifications and the data for the WLTC-cycle classes
and spits-out the attained speed-profile by the vehicle, along with it gear-shifts used
and any warnings.

An "execution" or a "run" of an experiment is depicted in the following diagram::

                       _______________
     .-------.        |               |      .------------------.
    / Model /-.   ==> |   Experiment  | ==> / Model(augmented) /
   '-------'  /   ==> |---------------|    '------------------'
     .-------'        |  .-----------.|
                      | / WLTC-data / |
                      |'-----------'  |
                      |_______________|

Usage:
======

A usage example::

    >> import wltc

    >> model = wltc.Model({
        "vehicle": {
            "mass":     1500,
            "v_max":    195,
            "p_rated":  100,
            "n_rated":  5450,
            "n_idle":   950,
            "n_min":    500,
            "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
            "resistance_coeffs":[100, 0.5, 0.04],
        }
    }

    >> experiment = wltc.Experiment(model)

    >> experiment.run()

    >> print(model.data['params'])
    >> print(model.data['cycle_run'])
    >> print(model.driveability_report())


For information on the model-data, check the schema::

    print(wltc.instances.model_schema())



@author: ankostis@gmail.com, Dec-2013, JRC, (c) AGPLv3 or later

'''

# wltc's setup.py
from setuptools import setup
import os

projname = 'wltc'
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
    with open(os.path.join(mydir, fname)) as fd:
        return fd.read()

setup(
    name = projname,
    packages = [projname],
#     package_data= {'projname': ['data/*.csv']},
    test_suite="wltc.test", #TODO: check setup.py testsuit indeed works.
    version = '.'.join(readversioninfo('_version.py')),
    description = __doc__.strip().split("\n")[0],
    author = "ankostis",
    author_email = "ankostis@gmail.com",
    url = "https://github.com/ankostis/wltc",
    license = "GNU Affero General Public License v3 or later (AGPLv3+)",
    keywords = ['wltc', 'cycles', 'emissions', 'simulation', 'vehicles', 'cars', 'nedc', 'driving', 'simulation'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = __doc__,
    install_requires = [
                      'numpy',
                      'jsonschema',
#                       'jsonpointer',
                      ],
    test_requires = [
                      'pandas',
                      ],
)
