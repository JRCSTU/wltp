#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import warnings
'''
Identify gear-ratios from engine-run cycles
'''

import sys
import logging
from io import StringIO 
import math
import numpy as np, pandas as pd
from scipy import signal
from scipy.cluster import vq
from matplotlib import pyplot as plt


def read_CycleRun(cycle_run_file):
    df = pd.DataFrame.from_csv(cycle_run_file, header=0, index_col=None)
    
    cols = list('NV')
    if len(set(cols) - set(df.columns)) != 0:
        if df.shape[1] != 2:
            raise ValueError("Expected (at least) 2-column dataset with 'V' [km/h] and 'N' [rpm] columns, got: %s" % df.columns)
        else:
            m = df.median(axis=0)
            df.columns = cols if m[0] > m[1] else reversed(cols) # Assume RPMs are bigger numbers.
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

    return peaks0, peaks3, h_points, h_centers

def identify_gear_ratios_by_kmeans(obs, code, **kmeans_kws):
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
    
    
#     w_obs = vq.whiten(obs)
#     w_guess = vq.whiten(code)
    w_obs = obs
    w_guess = code
    
    k = _1d_kmeans(w_obs, w_guess, guess_func=np.median, **kmeans_kws)
    
    k = k[0]
#     k = np.sort(k.flatten()) * np.std(obs) # De-whiten
    k = np.sort(k.flatten())
    
    return k




df = read_CycleRun('test/VNreal.csv')
ngears = 6


## Filter-data
#
df['R1'] = (df.N / df.V)## SpeedToVelocity
df['R2'] = (df.V / df.N) # Work with R2 because evenly spaced (not log), and 0 < R2 < 1
df0 = df[(df.V > 2) & (df.N > 200) & (df.R2 > 0)]
#df1 = outliers_filter_df(df0, ['R2']) # PROBLEMATIC!!
df1 = df0


bins = int(ngears+2) * 6 # Rougly 4 bins per gear plus 2 left & right.
#bins = int(math.sqrt(df.shape[0]) * ngears/10)
peaks_df, peaks_df1, h_points, h_centers = identify_gear_ratios_by_binning(df1.R2, bins=bins, ngears=ngears)
peaks_stv = 1/peaks_df1.ratio.values
print("peaks_stv: %s"%peaks_stv)


kmeans_ratios = identify_gear_ratios_by_kmeans(df1.R2.values, peaks_df1.ratio.values)
kmeans_stv = 1/kmeans_ratios
print("kmeans_stv: %s"%kmeans_stv)

fig = plt.figure(figsize=(18,5))

## Plot engine-points
##
ax1 = plt.subplot(1,3,1)
ax1.plot(df.V, df.N, 'k.', markersize=1)    ## Plot also ignored points
ax1.plot(df1.V, df1.N, 'g+', markersize=4)  ## Plot only good-points
for r in peaks_stv:
    ax1.plot([0, df1.V.max()], [0, df1.V.max()*r], 'b-', alpha=0.5)
for r in kmeans_stv:
    ax1.plot([0, df1.V.max()], [0, df1.V.max()*r], 'r-', alpha=0.5)
plt.ylim(0, df1.N.median() + 2*df1.N.mad())
plt.xlim(df1.V.median() - 2*df1.V.mad(), df1.V.median() + 2*df1.V.mad())


## Plot ratios's from Histogram
#
ax2 = plt.subplot(1,3,2)
ax2.plot(h_centers, h_points)
ax2.plot(peaks_df.ratio, peaks_df.population, 'ob', markersize=8, fillstyle='none')
ax2.plot(peaks_df1.ratio, peaks_df1.population, 'ob', markersize=8, fillstyle='full') ## Annotate top-#gears

## Plot Ratios fromn K-means
##
ax3 = plt.subplot(1,3,3)
R = df1.R2
ax3.plot(R, 'g.', markersize=1)
for r in peaks_df.ratio:
    plt.hlines(r, 0, R.shape[0], 'b', linestyle=':')
for r in peaks_df1.ratio:
    plt.hlines(r, 0, R.shape[0], 'b', linestyle='-.')
for r in kmeans_ratios:
    plt.hlines(r, 0, R.shape[0], 'r', linestyle='--')
plt.ylim(R.min(), R.max())
plt.xlim(0, R.shape[0])

plt.show()