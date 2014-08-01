#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
wltc module: WLTC gear-shift calculator
'''


from ._version import __version__
import semantic_version as semver


__copyright__       = "Copyright (C) 2013-2014 European Commission (JRC)"
__license__         = "EUPL 1.1+"
__version_info__    = semver.Version(__version__)  # Just to check author behaves :-)

__all__ = ['Experiment', 'model']
