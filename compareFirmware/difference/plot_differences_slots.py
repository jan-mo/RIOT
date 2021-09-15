#!/usr/bin/env python3.9

import json, os, math
import matplotlib.pyplot as plt

from __plot_functions import plot_bar


# used differencing algos
diff_algos = [ "diff", "bsdiff", "xdelta3", "rsync8", "rsync16", "rsync32", "detools_none", "detools_heat"] # "deltagen" # bdelta - not implemented right

### load data ###
with open("sizes_sorted_same_slots.save", 'r') as json_file:
    sizes_sorted_same = json.load(json_file)
with open("sizes_sorted_alternating_slots.save", 'r') as json_file:
    sizes_sorted_alternating = json.load(json_file)
with open("versions.save", 'r') as file:
    versions = json.load(file)

if "deltagen" in diff_algos:
    ### load deltagen data ###
    with open("deltagen_diff/sizes_sorted.save", 'r') as json_file:
        sizes_sorted_deltagen = json.load(json_file)

    ### combine the data ###
    if len(sizes_sorted_deltagen["samd20-xpro"]["deltagen"].keys()) == len(sizes_sorted["samd20-xpro"][diff_algos[0]].keys()):
        sizes_sorted["samd20-xpro"].update(sizes_sorted_deltagen["samd20-xpro"])
        sizes_sorted["samd21-xpro"].update(sizes_sorted_deltagen["samd21-xpro"])
    else:
        print("Error: Revisions in sizes_deltagen and sizes does not match!")
        exit()

### update same slot ### 

### SAMD20 bar plot ###
### slot0
labels = ["rev_00_rev_02","rev_02_rev_04","rev_04_rev_06","rev_06_rev_08","rev_08_rev_10"]

array_all = []
norm_all = []
for algo in diff_algos:
    revs = sizes_sorted_same["samd20-xpro"][algo].keys()
    array = []
    norm = []
    for rev in revs:
        if "slot0" not in rev:
            continue
        array.append(sizes_sorted_same["samd20-xpro"][algo][rev]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted_same["samd20-xpro"][algo][rev]["normalized"])   # normalizing data
        if sizes_sorted_same["samd20-xpro"][algo][rev]["check"] != "pass":
            print("Warning: SAMD20 " + algo + " " + rev + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, "SAMD20-xpro Differencing Algorithms updates in slot0")
fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, "SAMD20-xpro Differencing Algorithms updates in slot0 (normalized)", "size of difference / target size")

# save and close figures
fig_samd20.savefig("plots/slots/diffalgos_samd20_same_slot0.pdf")
fig_norm20.savefig("plots/slots/norm_diffalgos_samd20_same_slot0.pdf")
plt.close("all")

### slot1
labels = ["rev_01_rev_03","rev_03_rev_05","rev_05_rev_07","rev_07_rev_09","rev_09_rev_11"]

array_all = []
norm_all = []
for algo in diff_algos:
    revs = sizes_sorted_same["samd20-xpro"][algo].keys()
    array = []
    norm = []
    for rev in revs:
        if "slot1" not in rev:
            continue
        array.append(sizes_sorted_same["samd20-xpro"][algo][rev]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted_same["samd20-xpro"][algo][rev]["normalized"])   # normalizing data
        if sizes_sorted_same["samd20-xpro"][algo][rev]["check"] != "pass":
            print("Warning: SAMD20 " + algo + " " + rev + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, "SAMD20-xpro Differencing Algorithms updates in slot1")
fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, "SAMD20-xpro Differencing Algorithms updates in slot1 (normalized)", "size of difference / target size")

# save and close figures
fig_samd20.savefig("plots/slots/diffalgos_samd20_same_slot1.pdf")
fig_norm20.savefig("plots/slots/norm_diffalgos_samd20_same_slot1.pdf")
plt.close("all")

### SAMD21 bar plot ###
### slot0
labels = ["rev_00_rev_02","rev_02_rev_04","rev_04_rev_06","rev_06_rev_08","rev_08_rev_10"]

array_all = []
norm_all = []
for algo in diff_algos:
    revs = sizes_sorted_same["samd21-xpro"][algo].keys()
    array = []
    norm = []
    for rev in revs:
        if "slot0" not in rev:
            continue
        array.append(sizes_sorted_same["samd21-xpro"][algo][rev]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted_same["samd21-xpro"][algo][rev]["normalized"])   # normalizing data
        if sizes_sorted_same["samd21-xpro"][algo][rev]["check"] != "pass":
            print("Warning: SAMD21 " + algo + " " + rev + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd21, ax_samd21 = plot_bar(array_all, labels, diff_algos, "SAMD21-xpro Differencing Algorithms updates in slot0")
fig_norm21, ax_norm21 = plot_bar(norm_all, labels, diff_algos, "SAMD21-xpro Differencing Algorithms updates in slot0 (normalized)", "size of difference / target size")

# save and close figures
fig_samd21.savefig("plots/slots/diffalgos_samd21_same_slot0.pdf")
fig_norm21.savefig("plots/slots/norm_diffalgos_samd21_same_slot0.pdf")
plt.close("all")

### slot1
labels = ["rev_01_rev_03","rev_03_rev_05","rev_05_rev_07","rev_07_rev_09","rev_09_rev_11"]

array_all = []
norm_all = []
for algo in diff_algos:
    revs = sizes_sorted_same["samd21-xpro"][algo].keys()
    array = []
    norm = []
    for rev in revs:
        if "slot1" not in rev:
            continue
        array.append(sizes_sorted_same["samd21-xpro"][algo][rev]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted_same["samd21-xpro"][algo][rev]["normalized"])   # normalizing data
        if sizes_sorted_same["samd21-xpro"][algo][rev]["check"] != "pass":
            print("Warning: SAMD21 " + algo + " " + rev + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd21, ax_samd21 = plot_bar(array_all, labels, diff_algos, "SAMD21-xpro Differencing Algorithms updates in slot1")
fig_norm21, ax_norm21 = plot_bar(norm_all, labels, diff_algos, "SAMD21-xpro Differencing Algorithms updates in slot1 (normalized)", "size of difference / target size")

# save and close figures
fig_samd21.savefig("plots/slots/diffalgos_samd21_same_slot1.pdf")
fig_norm21.savefig("plots/slots/norm_diffalgos_samd21_same_slot1.pdf")
plt.close("all")








### update alternating slots ### 

### SAMD20 bar plot ###
labels = ["rev_00_rev_01","rev_01_rev_02","rev_02_rev_03","rev_03_rev_04","rev_04_rev_05","rev_05_rev_06","rev_06_rev_07","rev_07_rev_08","rev_08_rev_09","rev_09_rev_10","rev_10_rev_11"]

keys = ["rev_00_slot0_rev_01_slot1","rev_01_slot1_rev_02_slot0","rev_02_slot0_rev_03_slot1","rev_03_slot1_rev_04_slot0","rev_04_slot0_rev_05_slot1","rev_05_slot1_rev_06_slot0","rev_06_slot0_rev_07_slot1","rev_07_slot1_rev_08_slot0","rev_08_slot0_rev_09_slot1","rev_09_slot1_rev_10_slot0","rev_10_slot0_rev_11_slot1"]

array_all = []
norm_all = []
for algo in diff_algos:
    array = []
    norm = []
    for key in keys:
        key = algo + "_" + key
        array.append(sizes_sorted_alternating["samd20-xpro"][algo][key]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted_alternating["samd20-xpro"][algo][key]["normalized"])   # normalizing data
        if sizes_sorted_alternating["samd20-xpro"][algo][key]["check"] != "pass":
            print("Warning: SAMD20 " + algo + " " + key + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, "SAMD20-xpro Differencing Algorithms updates in alternating slots")
fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, "SAMD20-xpro Differencing Algorithms updates in alternating slots (normalized)", "size of difference / target size")

# save and close figures
fig_samd20.savefig("plots/slots/diffalgos_samd20_alternating.pdf")
fig_norm20.savefig("plots/slots/norm_diffalgos_samd20_alternating.pdf")
plt.close("all")

### SAMD21 bar plot ###
labels = ["rev_00_rev_01","rev_01_rev_02","rev_02_rev_03","rev_03_rev_04","rev_04_rev_05","rev_05_rev_06","rev_06_rev_07","rev_07_rev_08","rev_08_rev_09","rev_09_rev_10","rev_10_rev_11"]

keys = ["rev_00_slot0_rev_01_slot1","rev_01_slot1_rev_02_slot0","rev_02_slot0_rev_03_slot1","rev_03_slot1_rev_04_slot0","rev_04_slot0_rev_05_slot1","rev_05_slot1_rev_06_slot0","rev_06_slot0_rev_07_slot1","rev_07_slot1_rev_08_slot0","rev_08_slot0_rev_09_slot1","rev_09_slot1_rev_10_slot0","rev_10_slot0_rev_11_slot1"]

array_all = []
norm_all = []
for algo in diff_algos:
    array = []
    norm = []
    for key in keys:
        key = algo + "_" + key
        array.append(sizes_sorted_alternating["samd21-xpro"][algo][key]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted_alternating["samd21-xpro"][algo][key]["normalized"])   # normalizing data
        if sizes_sorted_alternating["samd21-xpro"][algo][key]["check"] != "pass":
            print("Warning: SAMD21 " + algo + " " + key + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, "SAMD21-xpro Differencing Algorithms updates in alternating slots")
fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, "SAMD21-xpro Differencing Algorithms updates in alternating slots (normalized)", "size of difference / target size")

# save and close figures
fig_samd20.savefig("plots/slots/diffalgos_samd21_alternating.pdf")
fig_norm20.savefig("plots/slots/norm_diffalgos_samd21_alternating.pdf")
plt.close("all")

print("Done!")
