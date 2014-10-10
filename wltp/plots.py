#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from matplotlib import cbook, cm, pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.mlab import ma
from matplotlib.pyplot import colorbar
from numpy import polyfit, polyval
from wltp import model
from wltp.test import wltp_db_tests as wltpdb

import numpy as np


## From http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
#
class MidPointNorm(Normalize):
    """
    A Normilaze that makes a "diverging" or "bipolar" Colormap, where its center point is important and 
    so that the values go over or under it.
    
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
            val = 2 * (val - 0.5)
            if val < 0: 
                return  val*abs(vmin-midpoint) + midpoint
            else:
                return  val*abs(vmax-midpoint) + midpoint




def aggregate_single_columns_means(gened_column, heinz_column):
    """
    Runs experiments and aggregates mean-values from one column of each (gened, heinz) file-sets. 
    """
    vehdata = wltpdb._run_the_experiments(transplant_original_gears=False, compare_results=False)
    

    res = wltpdb._vehicles_applicator(wltpdb.gened_fname_glob, lambda _, df_g, df_h:(
            df_g[gened_column].mean(), df_h[heinz_column].mean()))
    res.columns = ['gened', 'heinz']
    vehdata = vehdata.merge(res, how='inner', left_index=True, right_index=True).sort()
    return vehdata


def fit_straight_line(x, y):
    regress_poly = polyfit(x, y, 1)
    line_points = [x.min(), x.max()]
    
    return line_points, regress_poly


def plot_class_limits(axis, y):
    class_limits = model.get_class_pmr_limits()
    for limit in class_limits:
        plt.axvline(limit, color='y', linewidth=2)
    
    bbox = {'facecolor':'yellow', 'alpha':0.5, 'pad':4, 'linewidth':0}
    axis.text(class_limits[0], y, 'class1', style='italic', color='r',
        bbox=bbox, horizontalalignment='right', verticalalignment='top', alpha=0.8)
    axis.text(class_limits[0], y, 'class2', style='italic', color='r',
        bbox=bbox, horizontalalignment='left', verticalalignment='bottom', alpha=0.8)
    axis.text(class_limits[1], y, 'class3', style='italic', color='r',
        bbox=bbox, horizontalalignment='left', verticalalignment='top', alpha=0.8)



#############
### PLOTS ###


def pmr_n_scatter(axis, quantity, gened_column, heinz_column):
    color_diff = 'r'
    alpha = 0.8

    vehdata = aggregate_single_columns_means(gened_column, heinz_column)
    vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']


    ## Prepare axis
    #
    axis.set_xlabel(r'$PMR [W/kg]$')
    axis.set_ylabel(r'$%s$' % quantity)
#     for tl in axis.get_yticklabels():
#         tl.set_color('g')
    ax2 = axis.twinx()
    ax2.set_ylabel(r'$\Delta %s$' % quantity, color=color_diff)
    for tl in ax2.get_yticklabels():
        tl.set_color(color_diff)

    plot_class_limits(axis, vehdata.gened.min())
    
    ## Plot data
    #
    l_gened, = axis.plot(vehdata.pmr, vehdata.gened, 'ob', fillstyle='none', alpha=alpha)
    l_heinz, = axis.plot(vehdata.pmr, vehdata.heinz, '+g', markersize=8)
    
    mean_diffs = vehdata.gened - vehdata.heinz
    l_dp = ax2.plot(vehdata.pmr, mean_diffs, '.', color=color_diff, markersize=1.5)
    line_points, regress_poly = fit_straight_line(vehdata.pmr, mean_diffs)
    l_regress, = ax2.plot(line_points, polyval(regress_poly, line_points), '-', 
        color=color_diff, alpha=alpha/2)

    plt.legend([l_gened, l_heinz, l_regress], ['Python', 'Access-db', 'Diffrences'])
    plt.title("Means of %s vs Access-db(2sec rule)" % quantity)
    
    axis.xaxis.grid(True)
    axis.yaxis.grid(True)



def pmr_n_arrows(axis, axis_cbar , quantity, gened_column, heinz_column):
    color_diff = 'r'
    alpha = 0.9
    colormap = cm.PiYG  # @UndefinedVariable
    cm_norm = MidPointNorm()
    
    vehdata = aggregate_single_columns_means(gened_column, heinz_column)
    vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']
    vehdata['m_diff'] = vehdata.gened - vehdata.heinz


    ## Prepare axis
    #
    axis.set_xlabel(r'$PMR [W/kg]$')
    axis.set_ylabel(r'$%s$' % quantity)
#     for tl in axis.get_yticklabels():
#         tl.set_color('g')

    ax2 = axis.twinx()
    ax2.set_ylabel(r'$\Delta %s$' % quantity, color=color_diff)
    for tl in ax2.get_yticklabels():
        tl.set_color(color_diff)

    plot_class_limits(axis, vehdata.gened.min())
        
    ## Colormap legend
    #
    nsamples = 20
    m = np.linspace(vehdata.m_diff.min(), vehdata.m_diff.max(), nsamples)
    m.resize((nsamples, 1))
    axis_cbar.imshow(m, cmap=colormap, norm=cm_norm, aspect=2)
    axis_cbar.xaxis.set_visible(False)
    axis_cbar.yaxis.set_ticks_position('right')
    
    ## Plot data
    #
    q_heinz = axis.quiver(vehdata.pmr, vehdata.heinz, 0, vehdata.m_diff, 
        vehdata.m_diff, cmap=colormap, norm=cm_norm,
        units='inches', width=0.04, alpha=alpha, 
        pivot='tip'
    )
    
    l_gened, = axis.plot(vehdata.pmr, vehdata.gened, '+k', markersize=3, alpha=alpha)

    ax2.plot(vehdata.pmr, vehdata.m_diff, '.', color=color_diff, markersize=1.5)
    line_points, regress_poly = fit_straight_line(vehdata.pmr, vehdata.m_diff)
    l_regress, = ax2.plot(line_points, polyval(regress_poly, line_points), '-', 
        color=color_diff, alpha=alpha/2)


    plt.legend([l_gened, l_regress, ], ['Python', 'Diffrences'])
    plt.title(r"Python vs Access-db(2sec rule)")
    

    axis.xaxis.grid(True)
    axis.yaxis.grid(True)
