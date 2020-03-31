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

from readme_renderer import rst

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


########################
## Copied from Twine

# Regular expression used to capture and reformat docutils warnings into
# something that a human can understand. This is loosely borrowed from
# Sphinx: https://github.com/sphinx-doc/sphinx/blob
# /c35eb6fade7a3b4a6de4183d1dd4196f04a5edaf/sphinx/util/docutils.py#L199
_REPORT_RE = re.compile(
    r"^<string>:(?P<line>(?:\d+)?): "
    r"\((?P<level>DEBUG|INFO|WARNING|ERROR|SEVERE)/(\d+)?\) "
    r"(?P<message>.*)",
    re.DOTALL | re.MULTILINE,
)


class _WarningStream:
    def __init__(self):
        self.output = io.StringIO()

    def write(self, text):
        matched = _REPORT_RE.search(text)

        if not matched:
            self.output.write(text)
            return

        self.output.write(
            "line {line}: {level_text}: {message}\n".format(
                level_text=matched.group("level").capitalize(),
                line=matched.group("line"),
                message=matched.group("message").rstrip("\r\n"),
            )
        )


def test_README_as_PyPi_landing_page(monkeypatch):
    """Not executing `setup.py build-sphinx` to control log/stderr visibility with pytest"""
    long_desc = subprocess.check_output(
        "python setup.py --long-description".split(), cwd=proj_path
    )
    assert long_desc is not None, "Long_desc is null!"

    err_stream = _WarningStream()
    result = rst.render(
        long_desc,
        # The specific options are a selective copy of:
        # https://github.com/pypa/readme_renderer/blob/master/readme_renderer/rst.py
        stream=err_stream,
        halt_level=2,  # 2=WARN, 1=INFO
    )
    if not result:
        raise AssertionError(str(err_stream))


def test_sphinx_html():
    # Fail on warnings, but don't rebuild all files (no `-a`),
    subprocess.check_output("python setup.py build_sphinx -W".split(), cwd=proj_path)
