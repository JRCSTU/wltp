#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltcg.
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

'''The actual WLTC gear-shift calculator.

An "execution" or a "run" of an experiment is depicted in the following diagram::

                   _______________
     .-------.    |               |      .------------------.
    / Model / ==> |   Experiment  | ==> / Model(augmented) /
   '-------'      |---------------|    '------------------'
                  |  .-----------.|
                  | / WLTC-data / |
                  |'-----------'  |
                  |_______________|


@author: ankostis@gmail.com
@since: 1 Jan 2014
'''

from .schemas import wltc_validator
from .instances import (wltc_data) #, Model)

class Experiment(object):
    '''Runs the vehicle and cycle data describing a WLTC experiment. '''


    def __init__(self, model, validate_wltc = False):
        """
        ``model`` is a tree (formed by dicts & lists) holding the experiment data.

        ``skip_validation`` when true, does not validate the model.
        """

        if (validate_wltc):
            wltc_validator().validate(wltc_data())

