#!python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
Detects vehile's gear-ratios from cycle-data and reconstructs the gears-profile by identifying the actual gears used.

A "gear-ratio" is the inverse of the "engine-speed-to-velocity (STV)", which is 
the number of engine revolutions required, in RPM, in order for the the vehicle to travel with 1 km/h.

The "cycle-data" is a :class:`pd.DataFrame` containing (at least) `N` and `V` columns 
with [rpm] and [km/h] as units respectively.

The detection of the gear-ratios happens in a 3 steps, approximation or guessing, estimation and selection:

1. Produce a number of different *approximate* sets of gear-ratios (the "guesses") 
   by producing histograms of the ratios with different combinations of bins, and then 
   taking the first #gears of peaks.
2. Feed these "guessed" sets of gear-ratios into a robust (with median) kmeans clustering algorithm, and
3. pick the set which has the minimum distortion.

The identification of the actual gear on each cycle-data point (reconstructing the gear-profile) is based on 
the absolute-difference of its cycle-ratio with its nearest estimated gear-ratio, above.

.. Note: The inverse of STVs are used throughout the calculations here because they are usually equally spaced.
'''

from collections import namedtuple
import math
import numpy as np, pandas as pd
from scipy import signal
from matplotlib import pyplot as plt


def _outliers_filter_df(df, cols):
    for col in cols:
        mean = df[col].median()
        #std  = np.subtract(*np.percentile(df[col], [75, 25]))
        std  = df[col].mad()
        df = df[
            (df[col] >= mean - 2 * std) & 
            (df[col] <= mean + 2 * std)
        ]
    
    return df

def _filter_cycle(df, filter_outliers=None):
    ## Filter-data
    #
    df['R2'] = (df.V / df.N) # Work with R2 because evenly spaced (not log), and 0 < R2 < 1
    df0 = df[(df.V > 2) & (df.R2 > 0)]
    df1 = _outliers_filter_df(df0, ['R2']) if filter_outliers else df0 # PROBLEMATIC!!

    return df1


def _approximate_ratios_by_binning(ratios, bins, ngears):
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


def _norm1_1d_vq(obs, guess):
    """Simplified from scipy.cluster.vq.py_vq2()"""
    dist = np.abs(obs[np.newaxis, :] - guess[:, np.newaxis])
    code = np.argmin(dist, 0)
    min_dist = np.minimum.reduce(dist, 0)
    
    return code, min_dist

def _estimate_ratios_by_kmeans(obs, guess, **kmeans_kws):
    """
    Adapted kmeans to use norm1 distances (identical to euclidean-norm2 for 1D)
    and using median() for each guess, to ignore outliers and identify 
    "gear-lines".
    """
        
    def _1d_kmeans(obs, guess, guess_func, thresh=1e-5):
        """ The "raw" version of k-means, adapted from scipy.cluster.vq._kmeans(). """
    
        code_book = np.array(guess, copy=True)
        avg_dist = []
        diff = thresh+1.
        while diff > thresh:
            nc = code_book.size
            # compute membership and distances between obs and code_book
            obs_code, distort = _norm1_1d_vq(obs, code_book)
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


## The artifacts of each detection attempt. 
#
Detekt = namedtuple('Detekt', [
    'distort', 
    'guess', 'final', 
    'all_peaks_df', 'hist_X', 'hist_Y'
])
def _new_Detekt_approximation(guess_ratios, all_peaks_df, hist_X, hist_Y):
    return Detekt(None, guess_ratios, None, all_peaks_df, hist_X, hist_Y)
def _set_Detekt_final(gears, final_ratios, distortion):
    return gears._replace(distort=distortion, final=final_ratios)

def _append_aproximate_Detekt(ngears, cases, ratios, all_peaks_df, hist_X, hist_Y):
    """Appends 2 sets of ratios for each one specified as input, the 2nd one being a linspace between the min-max."""
    if ratios.size == ngears:
        cases.append(_new_Detekt_approximation(ratios, all_peaks_df, hist_X, hist_Y))
        cases.append(_new_Detekt_approximation(np.linspace(ratios.min(), ratios.max(), ngears), all_peaks_df, hist_X, hist_Y))

def _gather_guessed_Detekts(ngears, cycle_df):
    """Makes a number gear-ratios guesses based on histograms with different bin combinations. """

    guessed_detekts = [] ## A list-of-Detekt: 
    bins_cases = [
            (ngears+2) * 6, # Roughly 4 bins per gear plus 2 left & right.
            math.sqrt(cycle_df.shape[0]),
    ]
    for bins in bins_cases:
        all_peaks_df, peaks_df1, peaks_df2, hist_X, hist_Y = _approximate_ratios_by_binning(cycle_df.R2, bins=bins, ngears=ngears)
    
        _append_aproximate_Detekt(ngears, guessed_detekts, peaks_df1.ratio.values, all_peaks_df, hist_X, hist_Y)
        _append_aproximate_Detekt(ngears, guessed_detekts, peaks_df2.ratio.values, all_peaks_df, hist_X, hist_Y)
        
    ## Add linspace for the complete ratio-range 
    #    using the 1st Detekt as template.
    guessed_detekts.append(guessed_detekts[0]._replace(guess=np.linspace(cycle_df.R2.min(), cycle_df.R2.max(), ngears)))
    
    return guessed_detekts


def _gather_final_Detekts(ngears, cycle_df, guessed_gears):
    """
    :param pd.DataFrame cycle_df: a dataframe with `N` and `V` columns with units [rpm] and [km/h] respectively 
                        (or inferred by comparing the means of these 2 columns).
    """
    final_detekts = []
    for gears in guessed_gears:
        ratios, distort = _estimate_ratios_by_kmeans(cycle_df.R2.values, gears.guess)
        if ratios.size == ngears:
            final_detekts.append(_set_Detekt_final(gears, ratios, distort))
    final_detekts = sorted(final_detekts, key=lambda x: x.distort)

    return final_detekts


def run_gear_ratios_detections_on_cycle_data(ngears, cycle_df):
    """
    Invoke this one if you want to draw the results.
    
    :param pd.DataFrame cycle_df: it must contain (at least) `N` and `V` columns (units: [rpm] and [km/h] respectively)
    :return: a list of all :class:`Detekt` tuples sorted with the most probable ones at the the head,
                        needed.  Its 1st element is the solution
    """
    filtered_df     = _filter_cycle(cycle_df)
    guessed_detekts = _gather_guessed_Detekts(ngears, filtered_df)
    final_detekts   = _gather_final_Detekts(ngears, filtered_df, guessed_detekts)

    return final_detekts

def detect_gear_ratios_from_cycle_data(ngears, cycle_df):
    """
    Use a 2 step procedure if you want to plot the results, by invoking
    `run_gear_ratios_detections_on_cycle_data()` and `plot_idgears_results()` separately.
    
    :return: a :class:`ndarray` with the detected gear-ratios (for the STVs, inverse them) 
    """
    detekts = run_gear_ratios_detections_on_cycle_data(ngears, cycle_df)
    if not detekts[0].final is None:
        return detekts[0].final, detekts[0].distort
    else:
        raise Exception('Detection failed to estimate any gear-ratios!\n  All-Detekts(%s)' % detekts)


def identify_gears(cycle_ratios, gear_ratios):
    """
    Return arrays will miss NaNs!
    
    :param ndarray cycle_ratios: a single column array/list/ndarray  of ratios (STVs or inverse).
    :param ndarray gear_ratios: this list/ndarray of gear-ratios with len equal to the #gears
    :return: a 2-tuple, where [0] is the 0-based identified-gears, and 
                        [1] the distortion for each cycle-point.
    """
    cycle_ratios = np.asarray(cycle_ratios).flatten()
    nums = np.isfinite(cycle_ratios)
    gears, distort = _norm1_1d_vq(cycle_ratios[nums], np.asarray(gear_ratios).flatten())

    return gears, distort


def plot_idgears_results(cycle_df, detekt, fig=None, axes=None):
    """
    :param detekt: A Detekt-namedtuple with the data to plot
    """
    if not fig:
        fig = plt.figure(figsize=(18,5))
        fig.suptitle('Detekt: %s, Accuracy: %s (wltp-good: ~< 1e-3)'%(detekt.final, detekt.distort))
    
    if axes:
        ax1, ax2, ax3 = axes
    else:
        ax1 = plt.subplot(1,3,1)
        ax2 = plt.subplot(1,3,2)
        ax3 = plt.subplot(1,3,3)

    peaks_stv = (1/detekt.guess)
    kmeans_stv = (1/detekt.final)

    ## Plot engine-points
    ##
    ax1.plot(cycle_df.V, cycle_df.N, 'g+', markersize=4)
    for r in peaks_stv:
        ax1.plot([0, cycle_df.V.max()], [0, cycle_df.V.max()*r], 'b-', alpha=0.5)
    for r in kmeans_stv:
        ax1.plot([0, cycle_df.V.max()], [0, cycle_df.V.max()*r], 'r-', alpha=0.5)
    plt.ylim(0, cycle_df.N.median() + 2*cycle_df.N.mad())
    plt.xlim(cycle_df.V.median() - 2*cycle_df.V.mad(), cycle_df.V.median() + 2*cycle_df.V.mad())
    
    
    ## Plot ratios's Histogram
    #
    ax2.plot(detekt.hist_Y, detekt.hist_X)
    ax2.plot(detekt.all_peaks_df.ratio, detekt.all_peaks_df.population, 'ob', markersize=8, fillstyle='none')
    #ax2.plot(peaks_df.ratio, peaks_df.population, 'ob', markersize=8, fillstyle='full') ## Annotate top-#detekt
    # plt.hlines(detekt.all_peaks_df.population.mean() - detekt.all_peaks_df.population.mad(), 0, detekt.hist_Y.max(), 'g', linestyle='-')
    
    ## Scatter-plot Ratios
    ##
    R = cycle_df.R2
    ax3.plot(R, 'g.', markersize=1)
    for r in detekt.all_peaks_df.ratio:
        plt.hlines(r, 0, R.shape[0], 'b', linestyle=':')
    for r in detekt.final:
        plt.hlines(r, 0, R.shape[0], 'b', linestyle='-.')
    for r in detekt.final:
        plt.hlines(r, 0, R.shape[0], 'r', linestyle='--')
    plt.ylim(R.min(), R.max())
    plt.xlim(0, R.shape[0])

