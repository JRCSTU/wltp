#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
''''Setuptools script for *wltp*, the WLTC gear-shift calculator.

Install:
========

To install it, assuming you have download the sources,
do the usual::

    python setup.py install

Or get it directly from the PIP repository::

    pip3 install wltp
'''
## Got ideas for project-setup from many places, among others:
#    http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
#    http://python-packaging-user-guide.readthedocs.org/en/latest/current.html

from distutils.version import StrictVersion
import os, sys, io
import re

from setuptools import setup


## Fail early in ancient python-versions
#
py_verinfo = sys.version_info
py_sver = StrictVersion("%s.%s.%s" % py_verinfo[:3])
if py_verinfo[0] == 2 and py_sver < StrictVersion("2.7"):
    exit("Sorry, only Python >= 2.7 is supported!")
if py_verinfo[0] == 3 and py_sver < StrictVersion("3.3"):
    exit("Sorry, only Python >= 3.3 is supported!")
PY2 = py_verinfo[0] < 3

projname = 'wltp'
mydir = os.path.dirname(__file__)



## Version-trick to have version-info in a single place,
## taken from: http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
##
def read_project_version():
    fglobals = {}
    with io.open(os.path.join(mydir, projname, '_version.py')) as fd:
        exec(fd.read(), fglobals)  # To read __version__
    return fglobals['__version__']

def read_text_lines(fname):
    with io.open(os.path.join(mydir, fname)) as fd:
        return fd.readlines()

def yield_sphinx_only_markup(lines):
    """
    :param file_inp:     a `filename` or ``sys.stdin``?
    :param file_out:     a `filename` or ``sys.stdout`?`

    """
    substs = [
        ## Selected Sphinx-only Roles.
        #
        (r':abbr:`([^`]+)`',        r'\1'),
        (r':ref:`([^`]+)`',         r'`\1`_'),
        (r':term:`([^`]+)`',        r'**\1**'),
        (r':dfn:`([^`]+)`',         r'**\1**'),
        (r':(samp|guilabel|menuselection):`([^`]+)`',        r'``\2``'),


        ## Sphinx-only roles:
        #        :foo:`bar`   --> foo(``bar``)
        #        :a:foo:`bar` XXX afoo(``bar``)
        #
        #(r'(:(\w+))?:(\w+):`([^`]*)`', r'\2\3(``\4``)'),
        (r':(\w+):`([^`]*)`', r'\1(``\2``)'),


        ## Sphinx-only Directives.
        #
        (r'\.\. doctest',           r'code-block'),
        (r'\.\. plot::',            r'.. '),
        (r'\.\. seealso',           r'info'),
        (r'\.\. glossary',          r'rubric'),
        (r'\.\. figure::',          r'.. '),


        ## Other
        #
        (r'\|version\|',              r'x.x.x'),
    ]

    regex_subs = [ (re.compile(regex, re.IGNORECASE), sub) for (regex, sub) in substs ]

    def clean_line(line):
        try:
            for (regex, sub) in regex_subs:
                line = regex.sub(sub, line)
        except Exception as ex:
            print("ERROR: %s, (line(%s)"%(regex, sub))
            raise ex

        return line

    for line in lines:
        yield clean_line(line)



proj_ver = read_project_version()


readme_lines = read_text_lines('README.rst')
description = readme_lines[1]
long_desc = ''.join(yield_sphinx_only_markup(readme_lines))

install_deps = [
    'six',
    'jsonschema>=2.4',
    'jsonpointer',
#     'prefixtree', ## NOT INSTALLABLE in python 3.4: https://github.com/provoke-vagueness/prefixtree/issues/2
    'numpy',
    'pandas', #'openpyxl', 'xlrd',
    'matplotlib', #>=1.4', ## Let it mature some time more...
]
if PY2:
    install_deps += ['mock']




setup(
    name = projname,
    packages = ['wltp', 'wltp.cycles', 'wltp.test', ],
#     package_data= {'projname': ['data/*.csv']},
#     scripts = ['wltp.py'],
    version=proj_ver,
    test_suite='nose.collector',
    description=description,
    long_description=long_desc,
    author="Kostis Anagnostopoulos @ European Commission (JRC)",
    author_email="ankostis@gmail.com",
    url = "https://github.com/ankostis/wltp",
    license = "European Union Public Licence 1.1 or later (EUPL 1.1+)",
    keywords = [
         "automotive", "vehicle", "vehicles", "car", "cars", "fuel", "consumption", "gears", "gearshifs",
        "simulation", "simulator", "driving", "engine", "wltc", "UNECE", "standard",
    ],
    classifiers = [
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Development Status :: 3 - Alpha",
        'Natural Language :: English',
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    scripts = ['wltp.py'],
    install_requires = install_deps,
    setup_requires = [
        'setuptools>=3.4.4',
        'sphinx>=1.2', # >=1.3
        'sphinx_rtd_theme',
        'matplotlib',
        'coveralls',
    ],
    tests_require = [
        'nose',
        'coverage',
    ],
    include_package_data = True,
    zip_safe=True,
)



