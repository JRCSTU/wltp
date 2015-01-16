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
from wltp import model

import math
import numpy as np


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
        Normalize.__init__(self, vmin, vmax, clip)
        self.midpoint = midpoint

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip

        result, is_scalar = self.process_value(value)

        self.autoscale_None(result)
        vmin, vmax, midpoint = self.vmin, self.vmax, self.midpoint

        if not (vmin < midpoint < vmax):
            raise ValueError("Midpoint(%s) must be between minvalue(%s) and maxvalue(%s)!"%(midpoint, vmin, vmax))
        elif vmin == vmax:
            result.fill(0) # Or should it be all masked? Or 0.5?
        elif vmin > vmax:
            raise ValueError("Maxvalue(%s) must be bigger than minvalue(%s)!"%(vmin, vmax))
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


## From http://stackoverflow.com/questions/20924085/python-conversion-between-coordinates
#
def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def cartesians_to_polarDiffs(X1, Y1, X2, Y2):
    """
    Given 2 sets of 2D-points calcs the polar euclidean-distance  and angle from 2nd-pair of points to 1st-pair.
    """
    U = X2 - X1
    V = Y2 - Y1
    DIFF, ANGLE = cart2pol(U, V)
    return U, V, DIFF, ANGLE


#############
### PLOTS ###


def plot_xy_diffs_scatter(X, Y, X_REF, Y_REF, ref_label, data_label, diff_label=None,
            data_fmt="+k", data_kws={}, ref_fmt='.g', ref_kws={},
            title=None, x_label=None, y_label=None, axes_tuple=None,
            mark_sections='classes'):
    color_diff = 'r'
    alpha = 0.8

    _, _, DIFF, _ = cartesians_to_polarDiffs(X_REF, Y_REF, X, Y)
    if axes_tuple:
        (axes, twin_axis) = axes_tuple
    else:
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

    ## Plot data
    #
    l_ref = axes.plot(X_REF, Y_REF, ref_fmt, label=ref_label,
        alpha=alpha, **ref_kws)
    l_data = axes.plot(X, Y, data_fmt, label=data_label, **data_kws)

    twin_axis.plot(X, DIFF, '.', color=color_diff, markersize=1.5)
    line_points, regress_poly = fit_straight_line(X, DIFF)
    l_diff = twin_axis.plot(line_points, polyval(regress_poly, line_points), '-',
        color=color_diff, label=diff_label)

    return (axes, twin_axis), (l_data, l_ref, l_diff)




def plot_xy_diffs_arrows(X, Y, X_REF, Y_REF, data_label, ref_label=None,
            data_fmt="+k", data_kws={},
            diff_label=None, diff_fmt="-r", diff_cmap=cm.hsv, diff_kws={}, #@UndefinedVariable cm.PiYG
            title=None, x_label=None, y_label=None, 
            axes_tuple=None,
            mark_sections=None):
    color_diff = 'r'
    alpha = 0.9
    cm_norm = MidPointNorm()

    U, V, DIFF, ANGLE = cartesians_to_polarDiffs(X_REF, Y_REF, X, Y)
    
    if axes_tuple:
        (axes, twin_axis) = axes_tuple
    else:
        bottom = 0.1
        height = 0.8
        axes = plt.axes([0.1, bottom, 0.80, height])
        
        ## Prepare axes
        #
        axes.set_xlabel(x_label)
        axes.set_ylabel(r'$%s$' % y_label.replace('$',''))
        axes.xaxis.grid(True)
        axes.yaxis.grid(True)
    
        twin_axis = axes.twinx()
        twin_axis.set_ylabel(r'$\Delta %s$' % y_label.replace('$',''), color=color_diff, labelpad=0)
        twin_axis.tick_params(axis='y', colors=color_diff)
        twin_axis.yaxis.grid(True, color=color_diff)

        plt.title(title, axes=axes)
        axes_tuple = (axes, twin_axis)

        
    if mark_sections == 'classes':
        plot_class_limits(axes, Y.min())
    elif mark_sections == 'parts':
        raise NotImplementedError()

    ## Plot data
    #
    l_ref = axes.quiver(X, Y, U, V,
        ANGLE, cmap=diff_cmap, norm=cm_norm,
        scale_units='xy', angles='xy', scale=1, 
        width=0.004, alpha=alpha,
        pivot='tip'
    )
    
    l_data, = axes.plot(X, Y, data_fmt, label=data_label, **data_kws)
    l_data.set_picker(3)
    
    l_diff = twin_axis.plot(X, V, '.', color=color_diff, markersize=0.7)
    line_points, regress_poly = fit_straight_line(X, V)
    l_diff_fitted, = twin_axis.plot(line_points, polyval(regress_poly, line_points), diff_fmt, 
        label=diff_label, **diff_kws)

    return axes_tuple, (l_data, l_ref, l_diff, l_diff_fitted)

## http://stackoverflow.com/questions/13306519/get-data-from-plot-with-matplotlib
class DataCursor(object):
    """
    Use::
    
        fig.canvas.mpl_connect('pick_event', DataCursor(plt.gca()))
    """
    x, y = 0.0, 0.0
    xoffset, yoffset = -20, 20

    def __init__(self, ax=None, 
                 text_template='x: {x:0.2f}\ny: {y:0.2f}\n{txt}', 
                 annotations=None):
        self.ax = ax or plt.gca()
        self.text_template = text_template
        self.annotations = annotations or []
        self.annotation = ax.annotate(self.text_template, 
                xy=(self.x, self.y), xytext=(self.xoffset, self.yoffset), 
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                )
        self.annotation.set_visible(False)

    def __call__(self, event):
        if event.mouseevent.xdata is not None:
            try:
                ind = event.ind[0] if isinstance(event.ind, np.ndarray) else event.ind
                x = event.artist.get_xdata()[ind]
                y = event.artist.get_ydata()[ind]
                try:
                    annotation = self.annotations[ind]
                except:
                    annotation = ''
                self.annotation.xy = (event.mouseevent.xdata, event.mouseevent.ydata)
                self.annotation.set_text(self.text_template.format(x=x, y=y, txt=annotation))
                self.annotation.set_visible(True)
                event.canvas.draw()
            except:
                pass
