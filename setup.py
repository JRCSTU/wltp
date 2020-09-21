#!/usr/bin/env python# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""Setuptools script for *wltp*, the WLTC gear-shift calculator."""
# Got ideas for project-setup from many places, among others:
#    http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
#    http://python-packaging-user-guide.readthedocs.org/en/latest/current.html

import os, sys, io, re
import subprocess as sbp
import datetime as dt
from setuptools import setup, find_packages


# Fail early in ancient python-versions
#
py_ver = sys.version_info
if py_ver < (3, 6):
    exit("Sorry, Python3 >= 3.6 is supported! Not %s" % (py_ver,))

proj_name = "wltp"
mydir = os.path.dirname(__file__)


# Version-trick to have version-info in a single place,
# taken from: http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
##
def read_project_version():
    fglobals = {}
    with io.open(os.path.join(mydir, proj_name, "_version.py")) as fd:
        exec(fd.read(), fglobals)  # To read __version__
    return fglobals["__version__"]


def _ask_git_version(default: str) -> str:
    try:
        return sbp.check_output(
            "git describe --always".split(), universal_newlines=True
        ).strip()
    except Exception:
        return default


git_ver = _ask_git_version("x.x.x")


def read_text_lines(fname):
    with io.open(os.path.join(mydir, fname)) as fd:
        return fd.readlines()


def yield_rst_only_markup(lines):
    """
    :param file_inp:     a `filename` or ``sys.stdin``?
    :param file_out:     a `filename` or ``sys.stdout`?`

    """
    # fmt: off
    substs = [
        # Selected Sphinx-only Roles.
        #
        (r":abbr:`([^`]+)`",        r"\1"),
        (r":envvar:`([^`]+)`", r"``env[$\1]``"),
        (r":ref:`([^`]+)`",         r"ref:`\1`"),
        (r":term:`([^`]+)`",        r"**\1**"),
        (r":download:`([^`]+)`",    r"``\1``"),
        (r":dfn:`([^`]+)`",         r"**\1**"),
        (r":(samp|guilabel|menuselection|doc|file):`([^`]+)`",        r"\1(`\2`)"),

        ## Sphinx-only roles:
        #        :foo:`bar`   --> foo(``bar``)
        #        :a:foo:`bar` XXX afoo(``bar``)
        #
        #(r"(:(\w+))?:(\w+):`([^`]*)`", r"\2\3(``\4``)"),
        (r":(\w+):`([^`]*)`", r"\1(`\2`)"),


        # Sphinx-only Directives.
        #
        (r"\.\. doctest",           r"code-block"),
        (r"\.\. module",            r"code-block"),
        (r"\.\. currentmodule::",   r"currentmodule:"),
        (r"\.\. raw::",            r".. raw:"),
        (r"\.\. plot::",            r".. plot:"),
        (r"\.\. seealso",           r"info"),
        (r"\.\. glossary",          r"rubric"),
        (r"\.\. default-role::",    r".. default-role:"),
        (r"\.\. dispatcher::",      r"code-block"),
        (r"\.\. todo::",            r".. note:: TODO"),


        # Other
        #
        (r"\|version\|",            git_ver),
        (r"\|release\|",            git_ver),
        (r"\|today\|",              dt.datetime.now().isoformat()),
        (r"\.\. include:: AUTHORS", r"see: AUTHORS"),
        (r"\.\. \|br\| raw::",      r".. |br| raw: "),
        (r"\|br\|",                 r""),
    ]
    # fmt: on

    regex_subs = [(re.compile(regex, re.IGNORECASE), sub) for (regex, sub) in substs]

    def clean_line(line):
        try:
            for (regex, sub) in regex_subs:
                line = regex.sub(sub, line)
        except Exception as ex:
            print("ERROR: %s, (line(%s)" % (regex, sub))
            raise ex

        return line

    for line in lines:
        yield clean_line(line)


proj_ver = read_project_version()


readme_lines = read_text_lines("README.rst")
description = readme_lines[1].strip()
long_desc = "".join(yield_rst_only_markup(readme_lines))
# Trick from: http://peterdowns.com/posts/first-time-with-pypi.html
download_url = "https://github.com/ankostis/%s/tarball/v%s" % (proj_name, proj_ver)

plot_reqs = ["matplotlib"]
excel_reqs = ["xlwings; sys_platform == 'win32'"]
doc_reqs = [
    "sphinx>=2",
    "matplotlib",
    "graphtik[sphinx] >=5.7.0",
    "sphinx-jsonschema >= 1.16",
]
notebook_reqs = [
    "papermill",
    "jupytext",
    "nb_black",
    "ipympl",
    "qgrid >=1.3.0",  # compatible with pandas 1.0+
    "jupyter",  # papermill not fetching PY-kernel with jupyter-1.0.0
    "columnize",
    "oct2py",
]
test_reqs = (
    notebook_reqs
    + doc_reqs
    + [
        "docutils",
        "docopt",
        "matplotlib",
        "coveralls",
        "openpyxl",  # for pandas to write excel-files
        "pytest==5.3.5",  # Pinned due to sugar
        "pytest-sugar",
        "pytest-sphinx==0.2.1",  # Pinned due to API break 0.2.2
        "pytest-cov",
        "sphinx",
        "tables",  # pandas-IO for h5
        "readme-renderer",  # for PyPi landing-page check
        "wheel",
    ]
)
dev_reqs = (
    test_reqs
    + plot_reqs
    + excel_reqs
    + [
        "twine",
        "pylint",
        "mypy",
        # for VSCode autoformatting
        "black; python_version > '3.5'",
        # for git autoformatting
        "pre-commit",
        # for VSCode RST linting
        "doc8",
        # for VSCode refactoring
        "rope",
        "sphinx-autobuild",
    ]
)

setup(
    name=proj_name,
    version=proj_ver,
    description=description,
    long_description=long_desc,
    long_description_content_type="text/x-rst",
    author="JRC-SRU on behalf of UNECE's GearShifting TF",
    author_email="ankostis@gmail.com",
    url="https://github.com/JRCSTU/wltp",
    download_url=download_url,
    project_urls={
        "Documentation": "https://wltp.readthedocs.io/",
        "Release Notes": "https://wltp.readthedocs.io/en/latest/CHANGES.html",
        "Sources": "https://github.com/JRCSTU/wltp",
        "Bug Tracker": "https://github.com/JRCSTU/wltp/issues",
        "Live Demo": "https://mybinder.org/v2/gh/JRCSTU/wltp/master?urlpath=lab/tree/Notebooks/README.md",
    },
    license="European Union Public Licence 1.1 or later (EUPL 1.1+)",
    keywords=[
        "automotive",
        "vehicles",
        "light-Duty-Vehicles",
        "cars",
        "emissions",
        "fuel-consumption",
        "gears",
        "gearshift",
        "simulator",
        "driving",
        "engine",
        "WLTP",
        "WLTC",
        "NEDC",
        "UNECE",
        "standards",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    #     package_data= {'proj_name': ['data/*.csv']},
    #    package_data = {
    #        'wltp.excel': ['*.xlsm', '*.ico'],
    #    },
    python_requires=">=3.6",
    install_requires=[
        "contextvars; python_version < '3.7'",
        "dataclasses; python_version < '3.7'",
        "boltons",
        # 5.1.0 namedtuples results, 5.2.0 map inputs-->args, # 5.2.2 BugFixes;
        # 5.4 Sphinx; 5.6 check_if_incomplete(); 5.7 FIX sphinx, 6.1.0 new plot;
        # 7+ sfxed, 8+ re-moduled; 8.3: mapped-->keyword; 8.4: subclass-Sol;
        # 9.0.0 JSNOP,fnop,modifier; 10.0.0 implicit; auto-name pipes, jsonp=>modify;
        # 10.1.0 keyword renames returns-dict; 10.2.0 compose(exclude);
        # 10.3.0 concat-dfs_pos_callback(+overwrites), drop implicit-sfxed
        "graphtik >=10.3",
        "jsonschema",
        "numpy",
        "pandas >=1.0",  # BooleanDType ternary extension type
        "pandalone >=0.4",  # Pandel auto-nulls
        "ruamel.yaml",
        "scipy",
        "toolz",
    ],
    tests_require=test_reqs,
    # NOTE: update the list in README's QuickStart section
    extras_require={
        "plot": plot_reqs,
        "excel": excel_reqs,
        "all": dev_reqs,
        "dev": dev_reqs,
        "notebook": notebook_reqs,
        "test": test_reqs,
        "doc": doc_reqs,
    },
    entry_points={"console_scripts": ["wltp = wltp.cli:main"]},
    zip_safe=True,
    options={
        "build_sphinx": {"build_dir": "docs/_build"},
        "bdist_wheel": {"universal": True},
    },
)
