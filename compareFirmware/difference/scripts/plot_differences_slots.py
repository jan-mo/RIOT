#!/usr/bin/env python3.9

import json, os, math

from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_bar, plot_function_diff

###
### plots the differences of slots
### plots alternating slots ('_alteranting.pdf'), every second slot ('_second.pdf') and diagonal update ('_revision.pdf')
###

# used differencing algos
diff_algos = ["byte_diff", "rsync8", "rsync16", "rsync32", "bsdiff", "vcdiff",  "zdelta", "xdelta3", "detools_none", "detools_heat", "deltagen"]

### load data ###
with open("../output/sizes_sorted_same_slots.save", 'r') as json_file:
    sizes_sorted_same = json.load(json_file)
with open("../output/sizes_sorted_alternating_slots.save", 'r') as json_file:
    sizes_sorted_alternating = json.load(json_file)
with open("../output/versions.save", 'r') as file:
    versions = json.load(file)

### combine deltagen with alternating and same  ###
if "deltagen" in diff_algos:
    ### load deltagen data ###
    with open("../deltagen_diff/sizes_sorted_riotboot.save", 'r') as json_file:
        sizes_sorted_deltagen = json.load(json_file)

    ### combine the data ###
    if len(sizes_sorted_deltagen["samd20-xpro"]["deltagen"].keys()) >= (len(sizes_sorted_same["samd20-xpro"][diff_algos[0]].keys()) + len(sizes_sorted_alternating["samd20-xpro"][diff_algos[0]].keys())):
        # samd20-xpro
        board = "samd20-xpro"
        # adding alternating
        sizes_sorted_alternating[board]["deltagen"] = dict()
        keys_alternating = sizes_sorted_alternating["samd20-xpro"]["rsync8"].keys()
        for key in keys_alternating:
            # convert key in deltagen
            conv_key = "deltagen" + key[6:]
            sizes_sorted_alternating[board]["deltagen"][conv_key] = sizes_sorted_deltagen[board]["deltagen"][conv_key]
        # adding same_slots
        sizes_sorted_same[board]["deltagen"] = dict()
        keys_same = sizes_sorted_same[board]["rsync8"].keys()
        for key in keys_same:
            # convert key in deltagen
            conv_key = "deltagen" + key[6:]
            sizes_sorted_same[board]["deltagen"][conv_key] = sizes_sorted_deltagen[board]["deltagen"][conv_key]

        # samd21-xpro
        board = "samd21-xpro"
        # adding alternating
        sizes_sorted_alternating[board]["deltagen"] = dict()
        keys_alternating = sizes_sorted_alternating["samd20-xpro"]["rsync8"].keys()
        for key in keys_alternating:
            # convert key in deltagen
            conv_key = "deltagen" + key[6:]
            sizes_sorted_alternating[board]["deltagen"][conv_key] = sizes_sorted_deltagen[board]["deltagen"][conv_key]
        # adding same_slots
        sizes_sorted_same[board]["deltagen"] = dict()
        keys_same = sizes_sorted_same[board]["rsync8"].keys()
        for key in keys_same:
            # convert key in deltagen
            conv_key = "deltagen" + key[6:]
            sizes_sorted_same[board]["deltagen"][conv_key] = sizes_sorted_deltagen[board]["deltagen"][conv_key]
    else:
        print("Error: Revisions in sizes_deltagen_riotboot are not enough!")
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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd20_same_slot0.pdf", "../plots/slots/", "SAMD20-xpro Differencing Algorithms updates in slot0")

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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd20_same_slot1.pdf", "../plots/slots/", "SAMD20-xpro Differencing Algorithms updates in slot1")


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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd21_same_slot0.pdf", "../plots/slots/", "SAMD21-xpro Differencing Algorithms updates in slot0")

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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd21_same_slot1.pdf", "../plots/slots/", "SAMD21-xpro Differencing Algorithms updates in slot1")




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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd20_alternating.pdf", "../plots/slots/", "SAMD20-xpro Differencing Algorithms updates in alternating slots")


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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd21_alternating.pdf", "../plots/slots/", "SAMD21-xpro Differencing Algorithms updates in alternating slots")

print("Done!")
