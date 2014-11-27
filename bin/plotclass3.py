#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Plot the class3 diagram used in the documents and stores in project's ``docs/_static`` folder.

Invoked with 1 arg will draw diagram on screen and wait before ending.
Invoked with 2 args will additionally save image as well.
'''

from __future__ import division, print_function, unicode_literals

import sys, os, os.path as path

from matplotlib import pyplot as plt
from matplotlib.pyplot import pause
from wltp import model

import numpy as np


def make_class_fig(class_name, class_data):
    font_size = 8
    tick_size = 6.5

    ## Get cycle-data
    #
    c=np.array(class_data['cycle'])
    a = 1000 * np.gradient(c) / 3600
    t = np.arange(0, len(c))
    parts = class_data['parts']
    part_limits = [e+0.5 for (s, e) in parts[:-1]]

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Time (s): ', size=font_size)
    ax1.xaxis.set_label_coords(-0.06, -0.030)
    for tl in ax1.get_xticklabels():
        tl.set_size(tick_size)


    ax1.set_ylabel(r'Velocity ($km/h$)', color='b', size=font_size)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
        tl.set_size(tick_size)


    ax2 = ax1.twinx()
    ax2.set_ylabel(r'Acceleration ($m/\sec_2$)', color='m', size=font_size)
    for tl in ax2.get_yticklabels():
        tl.set_color('m')
        tl.set_size(tick_size)

    l_vel = ax2.plot(t, a, 'm-', alpha=0.3)[0]
    l_acc = ax1.plot(t, c, 'b-')[0]
#     plt.legend([l_vel, l_acc], ['Velocity', 'Acceleration'])

    plt.title('WLTC %s'%class_name,  size=9.5, weight='bold')

    ## Plot part-Limits
    #
    for limit in part_limits:
        l = plt.axvline(limit, color='r', linewidth=2)

    ## Add part-labels.
    #
    v_pos = 129.5 # trial'n error
    if class_name == 'class1': # Acceleration scale changes!!
        v_pos /= 2
    bbox={'facecolor':'red', 'alpha':0.5, 'pad':4, 'linewidth':0}
    txts = ['Low', 'Medium', 'High', 'ExtraHigh']
    txts_pos = [0] + part_limits #[0.40, 0.67, 0.85]

    for (txt, h_pos) in zip(txts, txts_pos):
        ax1.text(h_pos + 8, v_pos, txt, style='italic',
            bbox=bbox, size=8)


    ax1.grid()
    ax1.xaxis.grid = True
    ax1.yaxis.grid = True

    fig.set_size_inches(2 * 2 * 1.618, 2)

    return fig


if __name__ == '__main__':
    os.chdir(path.dirname(__file__))

    wltc_data = model._get_wltc_data()
    for (class_name, class_data) in wltc_data['classes'].items():
        fig = make_class_fig(class_name, class_data)

        img_fname = path.join('..', 'docs', '_static', 'wltc_%s.png'%class_name )

        nargs = len(sys.argv)
        if (nargs > 1):
            plt.show()
        if (nargs == 1 or nargs > 2):
            fig.savefig(img_fname, dpi=100)
            print('Stored image: %s'% img_fname)

