#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import os

from matplotlib import pyplot as plt
from wltp import plots
from wltp.test import wltp_db_tests as wltpdb


if __name__ == '__main__':
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))
    plots.pmr_n_scatter(
        axis=plt.subplot(111), 
        quantity='EngineSpeed [rpm]', 
        gened_column='rpm', 
        heinz_column='n'
    )
    plt.show()
    
