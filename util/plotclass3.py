#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from matplotlib.pyplot import pause
'''Plot the class3 image used in the documents.
:created: 3 Aug 2014
'''
import numpy as np
from matplotlib import pyplot as plt
from wltp.cycles import class3


## Get cycle-data
#
d=class3.class_data_b()
c=np.array(d['cycle'])
a = 1000 * np.gradient(c) / 3600
t = np.arange(0, len(c))
parts = d['parts']
part_limits = [e+0.5 for (s, e) in parts[:-1]]

fig, ax1 = plt.subplots()
ax1.plot(t, c, 'b-')
ax1.set_xlabel('Time (s)')


ax1.set_ylabel(r'Velocity ($km/h$)', color='b')
for tl in ax1.get_yticklabels():
    tl.set_color('b')


ax2 = ax1.twinx()
l = ax2.plot(t, a, 'm-', alpha=0.3)[0]
ax2.set_ylabel(r'Acceleration ($m/\sec_2$)', color='m')
for tl in ax2.get_yticklabels():
    tl.set_color('m')

## Plot part-Limits
#
for limit in part_limits:
    l = plt.axvline(limit, color='r', linewidth=2)

v_pos = 0.95
bbox={'facecolor':'red', 'alpha':0.5, 'pad':10}
txts = [ 'Low', 'Medium', 'High', 'Extra-high']
txts_pos = [0.15, 0.40, 0.67, 0.85]  # trial'n error

for (txt, h_pos) in zip(txts, txts_pos):
    ax1.text(h_pos, v_pos, txt, style='italic',
        transform=ax1.transAxes,
        bbox=bbox)

ax1.grid()
ax1.xaxis.grid = True
ax1.yaxis.grid = True

plt.show()
