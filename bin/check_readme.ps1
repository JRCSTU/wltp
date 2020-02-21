#!/bin/bash
#-*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl


## Checks that README has no RsT-syntactic errors.
# Since it is used by `setup.py`'s `description` if it has any errors,
# PyPi would fail parsing them, ending up with an ugly landing page,
# when uploaded.

&python setup.py bdist_wheel
&twine check dist/*
