#!/usr/bin/env python3.9

import json, os, math

from __plot_functions import plot_bar, plot_function


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
MCU = "samd20-xpro"
### slot0
# getting keys
keys_algo = sizes_sorted_same[MCU][diff_algos[0]]

# setting labels and key for all algos
labels = []
for key in keys_algo:
    if "slot0" not in key:
        continue
    tmp = key.split("_")
    labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    revs = sizes_sorted_same[MCU][algo].keys()
    key = []
    for rev in revs:
        if "slot0" not in rev:
            continue
        key.append(rev)
    keys[algo] = key

plot_function(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd20_same_slot0.pdf", "plots/slots/", "SAMD20-xpro Differencing Algorithms updates in slot0")

### slot1
labels = []
for key in keys_algo:
    if "slot1" not in key:
        continue
    tmp = key.split("_")
    labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    revs = sizes_sorted_same[MCU][algo].keys()
    key = []
    for rev in revs:
        if "slot1" not in rev:
            continue
        key.append(rev)
    keys[algo] = key

plot_function(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd20_same_slot1.pdf", "plots/slots/", "SAMD20-xpro Differencing Algorithms updates in slot1")


### SAMD21 bar plot ###
MCU = "samd21-xpro"
### slot0
# getting keys
keys_algo = sizes_sorted_same[MCU][diff_algos[0]]

# setting labels and key for all algos
labels = []
for key in keys_algo:
    if "slot0" not in key:
        continue
    tmp = key.split("_")
    labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    revs = sizes_sorted_same[MCU][algo].keys()
    key = []
    for rev in revs:
        if "slot0" not in rev:
            continue
        key.append(rev)
    keys[algo] = key

plot_function(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd21_same_slot0.pdf", "plots/slots/", "SAMD21-xpro Differencing Algorithms updates in slot0")

### slot1
labels = []
for key in keys_algo:
    if "slot1" not in key:
        continue
    tmp = key.split("_")
    labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    revs = sizes_sorted_same[MCU][algo].keys()
    key = []
    for rev in revs:
        if "slot1" not in rev:
            continue
        key.append(rev)
    keys[algo] = key

plot_function(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd21_same_slot1.pdf", "plots/slots/", "SAMD21-xpro Differencing Algorithms updates in slot1")




### update alternating slots ###

### SAMD20 bar plot ###
MCU = "samd20-xpro"
# getting keys
keys_algo = sizes_sorted_alternating[MCU][diff_algos[0]]

# setting labels and key for all algos
labels = []
for key in keys_algo:
    tmp = key.split("_")
    labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    keys[algo] = sizes_sorted_alternating[MCU][algo].keys()

plot_function(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd20_alternating.pdf", "plots/slots/", "SAMD20-xpro Differencing Algorithms updates in alternating slots")


### SAMD21 bar plot ###
MCU = "samd21-xpro"
# getting keys
keys_algo = sizes_sorted_alternating[MCU][diff_algos[0]]

# setting labels and key for all algos
labels = []
for key in keys_algo:
    tmp = key.split("_")
    labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    keys[algo] = sizes_sorted_alternating[MCU][algo].keys()

plot_function(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd21_alternating.pdf", "plots/slots/", "SAMD21-xpro Differencing Algorithms updates in alternating slots")

print("Done!")
