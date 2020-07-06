#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""Plot the class3 diagram used in the documents and stores in project's ``docs/_static`` folder.

Invoked with 1 arg will draw diagram on screen and wait before ending.
Invoked with 2 args will additionally save image as well.
"""

import os
import os.path as path
import sys

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import pause

from wltp import cycler, datamodel, vehicle


def make_class_fig(class_name, class_data):
    font_size = 8
    tick_size = 6.5

    ## Get cycle-data
    #
    # Typical car data
    test_mass, f0, f1, f2 = 1200, 0.3, 0.03, 0
    v = class_data["V_cycle"]
    a = -v.diff(-1)
    p_inert = vehicle.calc_inertial_power(v, a, test_mass, 0)
    p_resist = vehicle.calc_p_resist(v, f0, f1, f2)
    p = vehicle.calc_required_power(p_inert, p_resist)
    p *= v.max() / p.max()
    t = np.arange(0, len(v))
    part_limits = class_data["parts"]

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Time (s): ", size=font_size)
    ax1.xaxis.set_label_coords(-0.06, -0.030)
    for tl in ax1.get_xticklabels():
        tl.set_size(tick_size)

    ax1.set_ylabel(r"Velocity ($km/h$)", color="b", size=font_size)
    for tl in ax1.get_yticklabels():
        tl.set_color("b")
        tl.set_size(tick_size)

    ax2 = ax1.twinx()
    ax2.set_ylabel(r"Power required", color="m", size=font_size)
    ax2.set_yticklabels([])

    ax2.fill_between(t, 0, p, color="m", alpha=0.3)
    _l_acc = ax1.plot(t, v, "b-")[0]

    #     plt.legend([l_vel, l_acc], ['Velocity', 'Acceleration'])

    plt.title("WLTC %s" % class_name, size=9.5, weight="bold")

    ## Plot part-Limits
    #
    for limit in part_limits:
        _l = plt.axvline(limit, color="r", linewidth=2)

    ## Add part-labels.
    #
    # Trial'n error
    v_pos = 135
    bbox = {"facecolor": "red", "alpha": 0.5, "pad": 4, "linewidth": 0}
    txts = datamodel.get_class_part_names(class_name)
    txts_pos = [0] + part_limits  # [0.40, 0.67, 0.85]

    for (txt, h_pos) in zip(txts, txts_pos):
        ax1.text(
            h_pos + 18,  # trial'n error
            v_pos,
            txt,
            style="italic",
            bbox=bbox,
            size=8,
            va="top",
            ha="left",
        )

    ax1.grid()
    ax1.xaxis.grid = True
    ax1.yaxis.grid = True
    xlim = [0, 1800]  # kmh
    ax1.set_xlim(xlim)
    ylim = [0, 140]  # kmh
    ax1.set_ylim(ylim)
    ax2.set_ylim(ylim)

    fig.set_size_inches(2 * 2 * 1.618, 2)
    fig.tight_layout(pad=0)

    return fig


if __name__ == "__main__":
    os.chdir(path.dirname(__file__))

    wltc_data = datamodel.get_wltc_data()
    for (class_name, class_data) in wltc_data["classes"].items():
        fig = make_class_fig(class_name, class_data)

        img_fname = path.join("..", "docs", "_static", "wltc_%s.png" % class_name)

        nargs = len(sys.argv)
        if nargs > 1:
            plt.show()
        if nargs == 1 or nargs > 2:
            fig.savefig(img_fname, dpi=100)
            print("Stored image: %s" % img_fname)
