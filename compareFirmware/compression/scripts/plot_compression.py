#!/usr/bin/env python3.9

import json, os
import seaborn as sns; sns.set_theme()
import pandas as pd
import matplotlib.pyplot as plt

from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_line_compression, plot_bar_compression

### save compression values
with open("../output/compression_diagonal_samd20.save", 'r') as file:
    sizes_diag_samd20 = json.load(file)
with open("../output/compression_diagonal_samd21.save", 'r') as file:
    sizes_diag_samd21 = json.load(file)
with open("../output/sizes_compression_rev.save", 'r') as file:
    sizes_rev = json.load(file)

### define algos that should be plotted
def_diff_algos = ["byte_diff", "rsync8", "rsync16", "rsync32", "bsdiff", "zdelta", "detools_heat", "vcdiff", "xdelta3", "deltagen"]
def_compression = ["zlib", "gzip", "bzip2", "lzma", "heatshrink", "miniz"]


### compression of revisions
fig_rev_samd20, ax_rev_samd20 = plot_bar_compression(sizes_rev["samd20"], def_compression, "SAMD20-xpro Compression of Revisions", "mean compressed revision with std [%]", zoom=True)
fig_rev_samd20.savefig("../plots/comp_revisions_samd20.pdf")

fig_rev_samd21, ax_rev_samd21 = plot_bar_compression(sizes_rev["samd21"], def_compression, "SAMD21-xpro Compression of Revisions", "mean compressed revision with std [%]", zoom=True)
fig_rev_samd21.savefig("../plots/comp_revisions_samd21.pdf")

plt.close("all")


### Compression of patch files SAMD20
print("SAMD20")
# normal
fig_normal, ax_normal = plot_line_compression(sizes_diag_samd20["normal"], def_diff_algos, def_compression, "SAMD20-xpro Compression of Patch Files", "size of compressed patch file [%]", zoom=True)
fig_normal.savefig("../plots/comp_diff_normal_samd20.pdf")

# riotboot
fig_riotboot, ax_riotboot = plot_line_compression(sizes_diag_samd20["riotboot"], def_diff_algos, def_compression, "SAMD20-xpro Compression of Patch Files with Slots", "size of compressed patch file [%]", zoom=True)
fig_riotboot.savefig("../plots/comp_diff_riotboot_samd20.pdf")

plt.close("all")


### Compression of patch files SAMD21
print("SAMD21")
# normal
fig_normal, ax_normal = plot_line_compression(sizes_diag_samd21["normal"], def_diff_algos, def_compression, "SAMD21-xpro Compression of Patch Files", "size of compressed patch file [%]", zoom=True)
fig_normal.savefig("../plots/comp_diff_normal_samd21.pdf")

# riotboot
fig_riotboot, ax_samd20_riotboot = plot_line_compression(sizes_diag_samd21["riotboot"], def_diff_algos, def_compression, "SAMD21-xpro Compression of Patch Files with Slots", "size of compressed patch file [%]", zoom=True)
fig_riotboot.savefig("../plots/comp_diff_riotboot_samd21.pdf")

plt.close("all")

print("Done!")
