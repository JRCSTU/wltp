#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
Identify gear-ratios from engine-run cycles
'''

import sys
import logging
import warnings
from collections import namedtuple
from io import StringIO 
import math
import numpy as np, pandas as pd
from scipy import signal
from scipy.cluster import vq
from matplotlib import pyplot as plt


def read_CycleRun(cycle_run_file):
    df = pd.read_table(cycle_run_file, sep=',', index_col=None, comment='#', skiprows=2, header=None)
    c=0 #2,4,6
    df = df.iloc[1:, c:c+2]
    df = df.convert_objects(convert_numeric=True).dropna()
    
    cols = list('NV')
    if len(set(cols) - set(df.columns)) != 0:
        if df.shape[1] != 2:
            raise ValueError("Expected (at least) 2-column dataset with 'V' [km/h] and 'N' [rpm] columns, got: %s" % df.columns)
        else:
            m = df.median(axis=0)
            df.columns = cols if m.iloc[0] > m.iloc[1] else reversed(cols) # Assume RPMs are bigger numbers.
    return df

def outliers_filter_df(df, cols):
    for col in cols:
        mean = df[col].median()
        #std  = np.subtract(*np.percentile(df[col], [75, 25]))
        std  = df[col].mad()
        df = df[
            (df[col] >= mean - 2 * std) & 
            (df[col] <= mean + 2 * std)
        ]
    
    return df


def identify_gear_ratios_by_binning(ratios, bins, ngears):
    """
    :return: 3 sets of ratios:
                1. all peaks detected with bins specified
                2. the first #gears peaks 
                3. the first #gears peaks detected by binning the space between the previous #gears identified  
    """
    def find_peaks(df):
        h_points , bin_edges = np.histogram(df, bins=bins, density=True)
        h_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        peak_bins = signal.argrelmax(h_points, mode='clip')
        peak_bins = peak_bins[0]

        peaks = pd.DataFrame({'bin': peak_bins, 'ratio': h_centers[peak_bins], 'population': h_points[peak_bins]})
        peaks = peaks.sort(['population'], ascending=False)

        return peaks, h_points, h_centers

    peaks0, _, _ = find_peaks(ratios)
    #display(peaks0)
    
    peaks1 = peaks0[:ngears].sort(['ratio'], ascending=True) ## Keep #<gears> of most-populated bins.
    #display(peaks1)
    
    ## Re-bin with narrower X-to-bin.
    #
    r_min = peaks1['ratio'].min()
    r_max = peaks1['ratio'].max()
    gear_distance = (r_max - r_min) / ngears
    r_min -= gear_distance
    r_max += gear_distance
    peaks2, h_points, h_centers = find_peaks(ratios[(ratios >= r_min) & (ratios <= r_max)])
    #display(peaks2)
    
    peaks3 = peaks2[:ngears].sort(['ratio'], ascending=True) ## Keep #<gears> of most-populated bins.
    #display(peaks3)

    return peaks0, peaks1, peaks3, h_points, h_centers

def identify_gear_ratios_by_kmeans(obs, guess, **kmeans_kws):
    """
    Adapted kmeans to use norm1 distances (identical to euclidean-norm2 for 1D)
    and using median() for each guess, to ignore outliers and identify 
    "gear-lines".
    """
    def norm1_1d_vq(obs, guess):
        """Simplified from scipy.cluster.vq.py_vq2()"""
        dist = np.abs(obs[np.newaxis, :] - guess[:, np.newaxis])
        code = np.argmin(dist, 0)
        min_dist = np.minimum.reduce(dist, 0)
        
        return code, min_dist
        
    def _1d_kmeans(obs, guess, guess_func, thresh=1e-5):
        """ The "raw" version of k-means, adapted from scipy.cluster.vq._kmeans(). """
    
        code_book = np.array(guess, copy=True)
        avg_dist = []
        diff = thresh+1.
        while diff > thresh:
            nc = code_book.size
            # compute membership and distances between obs and code_book
            obs_code, distort = norm1_1d_vq(obs, code_book)
            avg_dist.append(np.mean(distort))
            # recalc code_book as centroids of associated obs
            if(diff > thresh):
                has_members = []
                for i in np.arange(nc):
                    cell_members = obs[obs_code == i]
                    if cell_members.size > 0:
                        code_book[i] = guess_func(cell_members)
                        has_members.append(i)
                # remove code_books that didn't have any members
                code_book = code_book[has_members]
            if len(avg_dist) > 1:
                diff = avg_dist[-2] - avg_dist[-1]
        # print avg_dist
        return code_book, avg_dist[-1]
    
    centers, distortion = _1d_kmeans(obs, guess, guess_func=np.median, **kmeans_kws)
    
    centers = np.sort(centers)
    
    return centers, distortion


Gears = namedtuple('Gears', ['distort', 'guess', 'final', 'all_peaks_df', 'hist_X', 'hist_Y'])
def _new_gears(guess_ratios, all_peaks_df, hist_X, hist_Y):
    return Gears(None, guess_ratios, None, all_peaks_df, hist_X, hist_Y)
def _set_gears_results(gears, final_ratios, distortion):
    return gears._replace(distort=distortion, final=final_ratios)

def append_new_guessed_gears(ngears, cases, ratios, all_peaks_df, hist_X, hist_Y):
    if ratios.size == ngears:
        cases.append(_new_gears(ratios, all_peaks_df, hist_X, hist_Y))
        cases.append(_new_gears(np.linspace(ratios.min(), ratios.max(), ngears), all_peaks_df, hist_X, hist_Y))

def filter_cycle(df):
    ## Filter-data
    #
    df['R1'] = (df.N / df.V)## SpeedToVelocity
    df['R2'] = (df.V / df.N) # Work with R2 because evenly spaced (not log), and 0 < R2 < 1
    df0 = df[(df.V > 2) & (df.R2 > 0)]
    #df1 = outliers_filter_df(df0, ['R2']) # PROBLEMATIC!!
    df1 = df0

    return df1

def identify_guesses(ngears, cycle_df):
    guessed_gears = [ ## A list-of-tuples: 
            _new_gears(np.linspace(cycle_df.R2.min(), cycle_df.R2.max(), ngears), None, None, None) ##TODO: Set hist-values on default guess.
    ]
    bins_cases = [
            (ngears+2) * 6, # Roughly 4 bins per gear plus 2 left & right.
            math.sqrt(df.shape[0]),
    ]
    for bins in bins_cases:
        all_peaks_df, peaks_df1, peaks_df2, hist_X, hist_Y = identify_gear_ratios_by_binning(cycle_df.R2, bins=bins, ngears=ngears)
    
        append_new_guessed_gears(ngears, guessed_gears, peaks_df1.ratio.values, all_peaks_df, hist_X, hist_Y)
        append_new_guessed_gears(ngears, guessed_gears, peaks_df2.ratio.values, all_peaks_df, hist_X, hist_Y)

    return guessed_gears


def identify_final_gears(ngears, cycle_df, guessed_gears):
    final_gears = []
    for gears in guessed_gears:
        ratios, distort = identify_gear_ratios_by_kmeans(cycle_df.R2.values, gears.guess)
        if ratios.size == ngears:
            final_gears.append(_set_gears_results(gears, ratios, distort))
    final_gears = sorted(final_gears, key=lambda x: x.distort)

    return final_gears


def plot_idgears_results(ngears, best_gears):
    fig = plt.figure(figsize=(18,5))
    fig.suptitle('Gears: %s, Accuracy: %s (wltp-good: ~< 1e-3)'%(best_gears.final, best_gears.distort*ngears))
    
    peaks_stv = (1/best_gears.guess)
    print("peaks_stv: %s"% peaks_stv)
    kmeans_stv = (1/best_gears.final)
    print("kmeans_stv: %s"% kmeans_stv)
    
    ## Plot engine-points
    ##
    ax1 = plt.subplot(1,3,1)
    ax1.plot(df.V, df.N, 'k.', markersize=1)    ## Plot also ignored points
    ax1.plot(df.V, df.N, 'g+', markersize=4)  ## Plot only good-points
    for r in peaks_stv:
        ax1.plot([0, df.V.max()], [0, df.V.max()*r], 'b-', alpha=0.5)
    for r in kmeans_stv:
        ax1.plot([0, df.V.max()], [0, df.V.max()*r], 'r-', alpha=0.5)
    plt.ylim(0, df.N.median() + 2*df.N.mad())
    plt.xlim(df.V.median() - 2*df.V.mad(), df.V.median() + 2*df.V.mad())
    
    
    ## Plot ratios's Histogram
    #
    ax2 = plt.subplot(1,3,2)
    ax2.plot(best_gears.hist_Y, best_gears.hist_X)
    ax2.plot(best_gears.all_peaks_df.ratio, best_gears.all_peaks_df.population, 'ob', markersize=8, fillstyle='none')
    #ax2.plot(peaks_df.ratio, peaks_df.population, 'ob', markersize=8, fillstyle='full') ## Annotate top-#gears
    # plt.hlines(best_gears.all_peaks_df.population.mean() - best_gears.all_peaks_df.population.mad(), 0, best_gears.hist_Y.max(), 'g', linestyle='-')
    
    ## Scatter-plot Ratios
    ##
    ax3 = plt.subplot(1,3,3)
    R = df.R2
    ax3.plot(R, 'g.', markersize=1)
    for r in best_gears.all_peaks_df.ratio:
        plt.hlines(r, 0, R.shape[0], 'b', linestyle=':')
    for r in best_gears.final:
        plt.hlines(r, 0, R.shape[0], 'b', linestyle='-.')
    for r in best_gears.final:
        plt.hlines(r, 0, R.shape[0], 'r', linestyle='--')
    plt.ylim(R.min(), R.max())
    plt.xlim(0, R.shape[0])
    
    
    plt.show()



df = read_CycleRun('test/VNreal.csv')
ngears = 5

df              = filter_cycle(df)
guessed_gears   = identify_guesses(ngears, df)
final_gears     = identify_final_gears(ngears, df, guessed_gears)

best_gears = final_gears[0]

print(best_gears)
print(final_gears)

plot_idgears_results(ngears, best_gears)
    
