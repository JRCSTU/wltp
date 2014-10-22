#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, print_function, unicode_literals

from matplotlib import cbook, cm, pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.mlab import ma
from numpy import polyfit, polyval

import numpy as np
from wltp import model


## From http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
#
class MidPointNorm(Normalize):
    """
    A "diverging" or "bipolar" Normalize for Colormaps on a central-point, with values going up or down.

    Example:

        norm = MidPointNorm(midpoint=3)
        imshow(X, norm=norm)
    """
    def __init__(self, midpoint=0, vmin=None, vmax=None, clip=False):
        Normalize.__init__(self,vmin, vmax, clip)
        self.midpoint = midpoint

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip

        result, is_scalar = self.process_value(value)

        self.autoscale_None(result)
        vmin, vmax, midpoint = self.vmin, self.vmax, self.midpoint

        if not (vmin < midpoint < vmax):
            raise ValueError("midpoint must be between maxvalue and minvalue.")
        elif vmin == vmax:
            result.fill(0) # Or should it be all masked? Or 0.5?
        elif vmin > vmax:
            raise ValueError("maxvalue must be bigger than minvalue")
        else:
            vmin = float(vmin)
            vmax = float(vmax)
            if clip:
                mask = ma.getmask(result)
                result = ma.array(np.clip(result.filled(vmax), vmin, vmax),
                                  mask=mask)

            # ma division is very slow; we can take a shortcut
            resdat = result.data

            #First scale to -1 to 1 range, than to from 0 to 1.
            resdat -= midpoint
            resdat[resdat>0] /= abs(vmax - midpoint)
            resdat[resdat<0] /= abs(vmin - midpoint)

            resdat /= 2.
            resdat += 0.5
            result = np.ma.array(resdat, mask=result.mask, copy=False)

        if is_scalar:
            result = result[0]
        return result

    def inverse(self, value):
        if not self.scaled():
            raise ValueError("Not invertible until scaled")
        vmin, vmax, midpoint = self.vmin, self.vmax, self.midpoint

        if cbook.iterable(value):
            val = ma.asarray(value)
            val = 2 * (val-0.5)
            val[val>0]  *= abs(vmax - midpoint)
            val[val<0] *= abs(vmin - midpoint)
            val += midpoint
            return val
        else:
            val = 2 * (value - 0.5)
            if val < 0:
                return  val*abs(vmin-midpoint) + midpoint
            else:
                return  val*abs(vmax-midpoint) + midpoint





def fit_straight_line(x, y):
    regress_poly = polyfit(x, y, 1)
    line_points = [x.min(), x.max()]

    return line_points, regress_poly


def plot_class_limits(axis, y):
    class_limits = model.get_class_pmr_limits()
    for limit in class_limits:
        plt.axvline(limit, color='y', linewidth=2)

    bbox = {'facecolor':'yellow', 'alpha':0.5, 'pad':4, 'linewidth':0}
    axis.text(0, y, 'class-1', style='italic', color='r',
        bbox=bbox, horizontalalignment='left', verticalalignment='top', alpha=0.8)
    axis.text(class_limits[0], y, 'class-2', style='italic', color='r',
        bbox=bbox, horizontalalignment='left', verticalalignment='bottom', alpha=0.8)
    axis.text(class_limits[1], y, 'class-3', style='italic', color='r',
        bbox=bbox, horizontalalignment='left', verticalalignment='top', alpha=0.8)


#def plot_class_parts_limits(axis, cls, y):
#    class_limits = model.get_class_parts_limits(cls)
#    for limit in class_limits:
#        plt.axvline(limit, color='y', linewidth=2)

#    ## Plot part-Limits
#    #
#    for limit in part_limits:
#        l = plt.axvline(limit, color='r', linewidth=2)
#
#        ## Add part-labels.
#        #
#        v_pos = 129.5 # trial'n error
#        if class_name == 'class1': # Acceleration scale changes!!
#            v_pos /= 2
#        bbox={'facecolor':'red', 'alpha':0.5, 'pad':4, 'linewidth':0}
#        txts = [ 'Low', 'Medium', 'High', 'Extra-high']
#        txts_pos = [0] + part_limits #[0.40, 0.67, 0.85]
#
#        for (txt, h_pos) in zip(txts, txts_pos):
#            ax1.text(h_pos + 8, v_pos, txt, style='italic',
#                bbox=bbox, size=8)


def calc_2D_diff_on_Y(X1, Y1, X2, Y2):
    """
    Given 2 sets of 2D-points calcs the euclidean distance from 2nd to 1st with sign  based on the Y axis.
    """
    U = X2 - X1
    V = Y2 - Y1
    DIFF = np.sqrt(U ** 2 + V ** 2)
    DIFF[V < 0] = -DIFF[V < 0]
    return U, V, DIFF


#############
### PLOTS ###


def plot_xy_diffs_scatter(X, Y, X_REF, Y_REF, ref_label, data_label, diff_label=None,
            data_fmt="+k", data_kws={}, ref_fmt='.g', ref_kws={},
            title=None, x_label=None, y_label=None, axes=None,
            mark_sections='classes'):
    color_diff = 'r'
    alpha = 0.8

    _, _, DIFF = calc_2D_diff_on_Y(X_REF, Y_REF, X, Y)
    if not axes:
        axes = plt.subplot(111)

        plt.title(title)

        ## Prepare axes
        #
        axes.set_xlabel(x_label)
        axes.set_ylabel(y_label)
        axes.xaxis.grid(True)
        axes.yaxis.grid(True)

        twin_axis = axes.twinx()
        twin_axis.set_ylabel(r'$\Delta %s$' % y_label.replace('$',''), color=color_diff)
        twin_axis.tick_params(axis='y', colors=color_diff)
        twin_axis.yaxis.grid(True, color=color_diff)

        if mark_sections == 'classes':
            plot_class_limits(axes, Y.min())
        elif mark_sections == 'parts':
            raise NotImplementedError()

    else:
        (axes, twin_axis) = axes

    ## Plot data
    #
    l_ref = axes.plot(X_REF, Y_REF, ref_fmt, label=ref_label,
        alpha=alpha, **ref_kws)
    l_data = axes.plot(X, Y, data_fmt, label=data_label, **data_kws)

    twin_axis.plot(X, DIFF, '.', color=color_diff, markersize=1.5)
    line_points, regress_poly = fit_straight_line(X, DIFF)
    l_diff = twin_axis.plot(line_points, polyval(regress_poly, line_points), '-',
        color=color_diff, alpha=alpha/2, label=diff_label)

    return (axes, twin_axis), (l_data, l_ref, l_diff)




def plot_xy_diffs_arrows(X, Y, X_REF, Y_REF, quantity_name, title, x_label, axis, axis_cbar,
            mark_sections='classes'):
    color_diff = 'r'
    alpha = 0.9
    colormap = cm.PiYG  # @UndefinedVariable
    cm_norm = MidPointNorm()

    plt.title(title)
    U, V, DIFF = calc_2D_diff_on_Y(X_REF, Y_REF, X, Y)

    ## Prepare axes
    #
    axis.set_xlabel(x_label)
    axis.set_ylabel(r'%s$' % quantity_name)
    axis.xaxis.grid(True)
    axis.yaxis.grid(True)

    ax2 = axis.twinx()
    ax2.set_ylabel(r'$\Delta %s$' % quantity_name, color=color_diff, labelpad=0)
    ax2.tick_params(axis='y', colors=color_diff)
    ax2.yaxis.grid(True, color=color_diff)

    if mark_sections == 'classes':
        plot_class_limits(axis, Y.min())
    elif mark_sections == 'parts':
        raise NotImplementedError()

    ## Plot data
    #
    q_heinz = axis.quiver(X, Y, U, V,
        DIFF, cmap=colormap, norm=cm_norm,
        units='inches', width=0.04, alpha=alpha,
        pivot='tip'
    )

    l_gened, = axis.plot(X, Y, '+k', markersize=3, alpha=alpha)

    ax2.plot(X, DIFF, '.', color=color_diff, markersize=1.5)
    line_points, regress_poly = fit_straight_line(X, DIFF)
    l_regress, = ax2.plot(line_points, polyval(regress_poly, line_points), '-',
        color=color_diff, alpha=alpha/2)

    plt.legend([l_gened, l_regress, ], ['Python', 'Differences'])

    ## Colormap legend
    #
    min_DIFF = DIFF.min()
    max_DIFF = DIFF.max()
    nsamples = 20
    m = np.linspace(min_DIFF, max_DIFF, nsamples)
    m.resize((nsamples, 1))
    extent = max_DIFF - min_DIFF
    axis_cbar.imshow(m, cmap=colormap, norm=cm_norm, aspect=600/extent, origin="lower",
        extent=[0, 12, min_DIFF, max_DIFF])
    axis_cbar.xaxis.set_visible(False)
    axis_cbar.yaxis.set_ticks_position('left')
    axis_cbar.tick_params(axis='y', colors=color_diff, direction='inout', pad=0, labelsize=10)

    ax2.set_ylim([min_DIFF, max_DIFF])      ## Sync diff axes.
    ###ax2.set_axis_off()                   ## NOTE: Hiding exis, hides grids!
    ax2.yaxis.set_ticklabels([])            ## NOTE: Turn it on, to check axes are indeed synced
