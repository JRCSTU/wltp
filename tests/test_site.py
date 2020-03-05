#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2015-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import io
import os.path as osp
import re
import subprocess
import sys

from docutils import core as dcore

import wltp
from wltp import cli

mydir = osp.dirname(__file__)
proj_path = osp.join(mydir, "..")
readme_path = osp.join(proj_path, "README.rst")


def test_README_version_reldate_opening():
    ver = wltp.__version__
    reldate = wltp.__updated__
    header_len = 20
    mydir = osp.dirname(__file__)
    ver_found = rdate_found = False
    with open(readme_path) as fd:
        for i, l in zip(range(header_len), fd):
            if ver in l:
                ver_found = True
            if reldate not in l:
                rdate_found = True

    if not ver_found:
        msg = "Version(%s) not found in README %s header-lines!"
        raise AssertionError(msg % (ver, header_len))
    if not rdate_found:
        msg = "RelDate(%s) not found in README %s header-lines!"
        raise AssertionError(msg % (reldate, header_len))


def test_README_version_from_cmdline(capsys):
    ver = wltp.__version__
    with open(readme_path) as fd:
        text = fd.read()
        try:
            cli.main(["--version"])
        except SystemExit:
            pass  ## Cancel argparse's exit()
        captured = capsys.readouterr()
        proj_ver = captured.out.strip()
        assert proj_ver
        assert proj_ver in text, (
            "Version(%s) not found in README cmd-line version-check!" % ver,
        )


def test_README_as_PyPi_landing_page(monkeypatch):
    long_desc = subprocess.check_output(
        "python setup.py --long-description".split(), cwd=proj_path
    )
    assert long_desc is not None, "Long_desc is null!"

    monkeypatch.setattr(sys, "exit", lambda *arg: None)
    dcore.publish_string(
        long_desc,
        enable_exit_status=False,
        settings_overrides={  # see `docutils.frontend` for more.
            "halt_level": 2  # 2=WARN, 1=INFO
        },
    )
