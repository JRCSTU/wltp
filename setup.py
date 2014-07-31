#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
''''wltp: A WLTC gear-shift calculator

A calculator of the gear-shifts profile for light-duty-vehicles (cars)
according to UN's draft on the Worldwide harmonized Light vehicles Test Procedures.

It accepts as input the car-specifications and a selection of a WLTC-cycle classes
and spits-out the attained speed-profile by the vehicle, along with it gear-shifts used
and any warnings.  It certainly does not calculate any CO2 emissions or other metrics.

An "execution" or a "run" of an experiment is depicted in the following diagram::


         .-------------------.    ______________        .-------------------.
        /        Model      /    | Experiment   |       / Model(augmented)  /
       /-------------------/     |--------------|      /-------------------/
      / +--vehicle        /  ==> |  .----------.| ==> / +...              /
     /  +--params        /       | / WLTC-data/ |    /  +--cycle_run     /
    /                   /        |'----------'  |   /                   /
    '------------------'         |______________|  '-------------------'

Install:
========

To install it, assuming you have download the sources,
do the usual::

    python setup.py install

Or get it directly from the PIP repository::

    pip3 install fuefit
'''

# wltp's setup.py
from setuptools import setup
#from cx_Freeze import Executable
#from cx_Freeze import setup
import os

projname = 'wltp'
mydir = os.path.dirname(__file__)

## Version-trick to have version-info in a single place,
## taken from: http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
##
def read_project_version(fname):
    fglobals = {'__version_info__':('x', 'x', 'x')} # In case reading the version fails.
    exec(open(os.path.join(mydir, projname, fname)).read(), fglobals)  # To read __version_info__
    return fglobals['__version__']

# Trick to use README file as long_description.
#  It's nice, because now 1) we have a top level README file and
#  2) it's easier to type in the README file than to put a raw string in below ...
def read_text_lines(fname):
    with open(os.path.join(mydir, fname)) as fd:
        return fd.read()
readme_lines = read_text_lines('README.txt')

setup(
    name = projname,
    packages = ['wltp', 'wltp.cycles', 'wltp.test', ],
#     package_data= {'projname': ['data/*.csv']},
#     scripts = ['wltp.py'],
    version=read_project_version('_version.py'),
    test_suite="wltp.test", #TODO: check setup.py testsuite indeed works.
    description=readme_lines[1],
    long_description='\n'.join(readme_lines),
    author="ankostis @ European Commission (JRC)",
    author_email="ankostis@gmail.com",
    url = "https://github.com/ankostis/wltp",
    license = "European Union Public Licence 1.1 or later (EUPL 1.1+)",
    keywords = [
        "LDVs", "UN", "UNECE", "cars", "fuel-consumption",
        "gears", "gearshifs", "rpm", "vehicles", "wltc", "wltp"
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires = [
        'semantic_version',
        'numpy',
        'jsonschema',
#         'jsonpointer',
#         'pandas',
#         'pint',
    ],
    options = {
        'build_exe': {
            "excludes": [
                "jsonschema", #!!!! Schemas do not work in library-zip, so needs manuall to copy directly into app-dir
                "numpy", "scipy", #!!!! lostesso
                "PyQt4", "PySide",
                "IPython", "numexpr",
                "pygments", "pyreadline", "jinja2",
                "setuptools",
                "statsmodels", "docutils",
                "xmlrpc", "pytz",
                "nose",
                "Cython", "pydoc_data", "sphinx", "docutils",
                "multiprocessing", "lib2to3", "_markerlib",
#                 #urllib<--email<--http<--pandas
#                 #distutils" <-- pandas.compat
            ],
            'includes': [
#                 'matplotlib.backends.backend_tkagg',
            ],
            'include_files': [
                ## MANUAL COPY into build/exe-dir
                ##     from: https://bitbucket.org/anthony_tuininga/cx_freeze/issue/43/import-errors-when-using-cx_freeze-with
                #  site_packages(32bit/64bit)/
                #    jsonschema
                #    numpy
                #    scipy
            ],
        }, 'bdist_msi': {
            'add_to_path': False,
        },
    },
#     executables=[Executable("wltp.py", )], #base="Win32GUI")],
)
