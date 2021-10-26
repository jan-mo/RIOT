#!/usr/bin/env python3.9

import json, os
import seaborn as sns; sns.set_theme()
import pandas as pd
import matplotlib.pyplot as plt

from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_line_compression, plot_bar_compression, __convert_name_to_json_string

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
fig_rev_samd20, ax_rev_samd20 = plot_bar_compression(sizes_rev["samd20"], def_compression, "SAMD20-xpro Mean and STD of Compressed Revisions", "compressed revisions / target size", zoom=True)
fig_rev_samd20.savefig("../plots/comp_revisions_samd20.pdf")

fig_rev_samd21, ax_rev_samd21 = plot_bar_compression(sizes_rev["samd21"], def_compression, "SAMD21-xpro Mean and STD of Compressed Revisions", "compressed revisions / target size", zoom=True)
fig_rev_samd21.savefig("../plots/comp_revisions_samd21.pdf")

plt.close("all")


### Compression of patch files SAMD20
print("SAMD20")
# normal
fig_normal, ax_normal = plot_line_compression(sizes_diag_samd20["normal"], def_diff_algos, def_compression, "SAMD20-xpro Mean and STD of Compressed Patch Files", "compressed patch files / patch file size", zoom=True)
fig_normal.savefig("../plots/comp_diff_normal_samd20.pdf")

# riotboot
fig_riotboot, ax_riotboot = plot_line_compression(sizes_diag_samd20["riotboot"], def_diff_algos, def_compression, "SAMD20-xpro Mean and STD of Compressed Patch Files with Slots", "compressed patch file / patch file size", zoom=True)
fig_riotboot.savefig("../plots/comp_diff_riotboot_samd20.pdf")

# compare compression and target file
sizes_new_samd20 = dict()
sizes_new_samd20["normal"] = sizes_diag_samd20["normal"]
sizes_new_samd20["riotboot"] = sizes_diag_samd20["riotboot"]
for comp in def_compression:
    comp = __convert_name_to_json_string(comp)
    for diff in def_diff_algos:
        diff = __convert_name_to_json_string(diff)
        for value in sizes_diag_samd20["normal"][diff][comp]:
            split_value = value.split("_")
            rev = split_value[-2] + "_" + split_value[-1]
            sizes_new_samd20["normal"][diff][comp][value]["reduction"] = round(sizes_diag_samd20["normal"][diff][comp][value]["size_comp"] / sizes_rev["samd20"][comp][rev]["size_orig"], 2)
        for value in sizes_diag_samd20["riotboot"][diff][comp]:
            split_value = value.split("_")
            rev = split_value[-3] + "_" + split_value[-2]
            sizes_new_samd20["riotboot"][diff][comp][value]["reduction"] = round(sizes_diag_samd20["riotboot"][diff][comp][value]["size_comp"] / sizes_rev["samd20"][comp][rev]["size_orig"], 2)

fig_normal, ax_normal = plot_line_compression(sizes_new_samd20["normal"], def_diff_algos, def_compression, "SAMD20-xpro Mean and STD of Compressed Patch Files (normalized)", "compressed patch files / target size", zoom=True)
fig_riotboot, ax_riotboot = plot_line_compression(sizes_new_samd20["riotboot"], def_diff_algos, def_compression, "SAMD20-xpro Size of Compressed Patch Files with Slots (normalized)", "compressed patch file / target size", zoom=True)
fig_normal.savefig("../plots/comp_diff_normal_samd20_normalized.pdf")
fig_riotboot.savefig("../plots/comp_diff_riotboot_samd20_normalized.pdf")

plt.close("all")


### Compression of patch files SAMD21
print("SAMD21")
# normal
fig_normal, ax_normal = plot_line_compression(sizes_diag_samd21["normal"], def_diff_algos, def_compression, "SAMD21-xpro Mean and STD of Compressed Patch Files", "compressed patch file / patch file size", zoom=True)
fig_normal.savefig("../plots/comp_diff_normal_samd21.pdf")

# riotboot
fig_riotboot, ax_samd20_riotboot = plot_line_compression(sizes_diag_samd21["riotboot"], def_diff_algos, def_compression, "SAMD21-xpro Mean and STD of Compressed Patch Files with Slots", "compressed patch file / patch file size", zoom=True)
fig_riotboot.savefig("../plots/comp_diff_riotboot_samd21.pdf")

# compare compression and target file
sizes_new_samd21 = dict()
sizes_new_samd21["normal"] = sizes_diag_samd21["normal"]
sizes_new_samd21["riotboot"] = sizes_diag_samd21["riotboot"]
for comp in def_compression:
    comp = __convert_name_to_json_string(comp)
    for diff in def_diff_algos:
        diff = __convert_name_to_json_string(diff)
        for value in sizes_diag_samd21["normal"][diff][comp]:
            split_value = value.split("_")
            rev = split_value[-2] + "_" + split_value[-1]
            sizes_new_samd21["normal"][diff][comp][value]["reduction"] = round(sizes_diag_samd21["normal"][diff][comp][value]["size_comp"] / sizes_rev["samd21"][comp][rev]["size_orig"], 2)
        for value in sizes_diag_samd21["riotboot"][diff][comp]:
            split_value = value.split("_")
            rev = split_value[-3] + "_" + split_value[-2]
            sizes_new_samd21["riotboot"][diff][comp][value]["reduction"] = round(sizes_diag_samd21["riotboot"][diff][comp][value]["size_comp"] / sizes_rev["samd21"][comp][rev]["size_orig"], 2)

fig_normal, ax_normal = plot_line_compression(sizes_new_samd21["normal"], def_diff_algos, def_compression, "SAMD21-xpro Mean and STD of Compressed Patch Files (normalized)", "compressed patch files / target size", zoom=True)
fig_riotboot, ax_riotboot = plot_line_compression(sizes_new_samd21["riotboot"], def_diff_algos, def_compression, "SAMD21-xpro Mean and STD of Compressed Patch Files with Slots (normalized)", "compressed patch file / target size", zoom=True)
fig_normal.savefig("../plots/comp_diff_normal_samd21_normalized.pdf")
fig_riotboot.savefig("../plots/comp_diff_riotboot_samd21_normalized.pdf")

plt.close("all")

print("Done!")
