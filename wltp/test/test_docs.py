#! python
# -*- coding: UTF-8 -*-
#
# Copyright 2015-2016 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import io
import re
import subprocess
import unittest
from unittest.mock import patch

from wltp import __main__ as cmain
import wltp

import os.path as osp


mydir = osp.dirname(__file__)
proj_path = osp.join(mydir, '..', '..')
readme_path = osp.join(proj_path, 'README.rst')


class Doctest(unittest.TestCase):

    def test_README_version_reldate_opening(self):
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

    def test_README_version_from_cmdline(self):
        ver = wltp.__version__
        mydir = osp.dirname(__file__)
        with open(readme_path) as fd:
            ftext = fd.read()
            with patch('sys.stdout', new=io.StringIO()) as stdout:
                try:
                    cmain.main(['--version'])
                except SystemExit as ex:
                    pass ## Cancel docopt's exit()
            proj_ver = stdout.getvalue().strip()
            assert proj_ver
            self.assertIn(proj_ver, ftext,
                          "Version(%s) not found in README cmd-line version-check!" %
                          ver)

    def test_README_as_PyPi_landing_page(self):
        from docutils import core as dcore

        long_desc = subprocess.check_output(
                'python setup.py --long-description'.split(),
                cwd=proj_path)
        self.assertIsNotNone(long_desc, 'Long_desc is null!')

        with patch('sys.exit'):
            dcore.publish_string(long_desc, enable_exit_status=False,
                    settings_overrides={ # see `docutils.frontend` for more.
                            'halt_level': 2 # 2=WARN, 1=INFO
                    })

