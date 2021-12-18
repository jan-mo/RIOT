#!/usr/bin/env python3

import json, os, math
import matplotlib.pyplot as plt
import numpy as np


from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_bar, plot_function_diff, plot_function_diff_relative

###
### script plots all differences in revisions
### the plots are stored in 'plots/'
### calculates difference between one revision and all other plots
### plots the chunks from matches_diff against diagonal revision
###

# used differencing algos
diff_algos = ["baseline", "rsync8", "rsync16", "rsync32", "bsdiff", "vcdiff",  "zdelta", "xdelta3", "detools_heat", "deltagen"]


### load data revisions ###
with open("../output/sizes_sorted_alternating_slots.save", 'r') as json_file:
    sizes_sorted_alternating = json.load(json_file)
with open("../output/versions.save", 'r') as file:
    versions = json.load(file)


### load data matches_diff ###
with open("../../matches_diff/output/diffs_matches.save", 'r') as json_file:
    diffs_matches = json.load(json_file)

### get all chunks
chunks = []
for elem in diffs_matches["samd21-xpro"]["slots"]["alternating"]:
	chunks.append(diffs_matches["samd21-xpro"]["slots"]["alternating"][elem]["chunks"])


print(chunks)



fig, ax = plt.subplots()

x = [1,2,3,10]
y = [2,3,3,2]


plt.plot(x, y)



# Add some text for labels, title and custom x-axis tick labels, etc.
x = np.arange(0,20,10)  # the label locations
ax.set_xticks(x)
ax.set_xticklabels(x, rotation=45)
ax.legend(ncol=3, loc = 'upper center')
ax.legend(ncol=3, loc = 'upper right')

fig.tight_layout()


plt.show()