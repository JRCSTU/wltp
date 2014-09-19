#!/bin/bash
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl


## Always invokes  code-tests, but skip doctests and coverage on Python-2.


my_dir=`dirname "$0"`
cd $my_dir/..

if  python -c 'import sys; print(sys.version_info[0])'| grep -q '3'; then
    echo "Python-3: Running ALL tests (code-tests, doctests, coverage)."
    python setup.py test_all
else
    echo "Python-2: Running ONLY code-tests."
    python setup.py test_code
fi

