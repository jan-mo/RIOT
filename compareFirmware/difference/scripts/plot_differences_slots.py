#!/usr/bin/env python3

import json, os, math

from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_bar, plot_function_diff

###
### plots the differences of slots
### plots alternating slots ('_alteranting.pdf'), every second slot ('_second.pdf') and diagonal update ('_revision.pdf')
###

# used differencing algos
diff_algos = ["baseline", "rsync8", "rsync16", "rsync32", "bsdiff", "vcdiff",  "zdelta", "xdelta3", "detools_heat", "deltagen"]
#diff_algos = ["minibs_heat", "bsdiff", "zdelta", "detools_heat", "vcdiff"]

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
print("SAMD20")
### slot0 and slot1
# getting keys
keys_algo = sizes_sorted_same[MCU][diff_algos[0]]

# setting labels and key for all algos
labels = []
for key in keys_algo:
    if "slot0" in key or "slot1" in key:
        tmp = key.split("_")
        labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    revs = sizes_sorted_same[MCU][algo].keys()
    key = []
    for rev in revs:
        if "slot0" in rev or "slot1" in rev:
            key.append(rev)
    keys[algo] = key

plot_function_diff(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd20_same_slot0_slot1.pdf", "../plots/slots/", False, zoom = True)


### SAMD21 bar plot ###
MCU = "samd21-xpro"
print("SAMD21")
### slot0
# getting keys
keys_algo = sizes_sorted_same[MCU][diff_algos[0]]

# setting labels and key for all algos
labels = []
for key in keys_algo:
    if "slot0" in key or "slot1" in key:
        tmp = key.split("_")
        labels.append(tmp[-6] + tmp[-5] + "_" + tmp[-3] + tmp[-2])

keys = dict()
for algo in diff_algos:
    revs = sizes_sorted_same[MCU][algo].keys()
    key = []
    for rev in revs:
        if "slot0" in rev or "slot1" in rev:
            key.append(rev)
    keys[algo] = key

plot_function_diff(diff_algos, keys, labels, sizes_sorted_same, MCU, "diffalgos_samd21_same_slot0_slot1.pdf", "../plots/slots/", False, zoom = True)




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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd20_alternating.pdf", "../plots/slots/", False, zoom = True)


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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd21_alternating.pdf", "../plots/slots/", False, zoom = True)






############## Evaluation #################
### update alternating slots Evaluation ###
diff_algos = ["minibs_heat", "bsdiff", "zdelta", "detools_heat", "vcdiff"]

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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd20_minidiff.pdf", "../plots/slots/", False, zoom = True)


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

plot_function_diff(diff_algos, keys, labels, sizes_sorted_alternating, MCU, "diffalgos_samd21_minidiff.pdf", "../plots/slots/", False, zoom = True)








######### plot chunks against diff

### load data matches_diff ###
with open("../../matches_diff/output/diffs_matches.save", 'r') as json_file:
    diffs_matches = json.load(json_file)


### get all chunks
chunks = []
added = []
deleted = []
size = []
for elem in diffs_matches["samd21-xpro"]["slots"]["alternating"]:
    chunks.append(diffs_matches["samd21-xpro"]["slots"]["alternating"][elem]["chunks"])
    added.append(diffs_matches["samd21-xpro"]["slots"]["alternating"][elem]["added"])
    deleted.append(diffs_matches["samd21-xpro"]["slots"]["alternating"][elem]["deleted"])
    size.append(diffs_matches["samd21-xpro"]["slots"]["alternating"][elem]["size"])

### combine keys and characteristics
chunks_comb = []
added_comb = []
deleted_comb = []
size_comb = []
j = 0
for algo in diff_algos:
    j = j + 1
    for i, elem in enumerate(keys[algo]):
        chunks_comb.append([j, chunks[i], elem])
        added_comb.append([j, added[i], elem])
        deleted_comb.append([j, deleted[i], elem])
        size_comb.append([j, size[i], elem])

chunks_comb.sort()
added_comb.sort()
deleted_comb.sort()
size_comb.sort()

### decombine the elements
keys_sorted_chunks = dict()
keys_sorted_added = dict()
keys_sorted_deleted = dict()
keys_sorted_size = dict()
for i, algo in enumerate(diff_algos):
    keys_sorted_chunks[algo] = dict()
    keys_sorted_added[algo] = dict()
    keys_sorted_deleted[algo] = dict()
    keys_sorted_size[algo] = dict()
    key_chunks = []
    key_added = []
    key_deleted = []
    key_size = []
    for j in range(len(versions)-1):
        key_chunks.append(chunks_comb[j+i*(len(versions)-1)][2])
        key_added.append(added_comb[j+i*(len(versions)-1)][2])
        key_deleted.append(deleted_comb[j+i*(len(versions)-1)][2])
        key_size.append(size_comb[j+i*(len(versions)-1)][2])
    keys_sorted_chunks[algo] = key_chunks
    keys_sorted_added[algo] = key_added
    keys_sorted_deleted[algo] = key_deleted
    keys_sorted_size[algo] = key_size


chunks.sort()
added.sort()
deleted.sort()
size.sort()

### chunks
plot_function_diff(diff_algos, keys_sorted_chunks, chunks, sizes_sorted_alternating, MCU, "chunks_diff_samd21_alternating.pdf", "../plots/", False, zoom = True, ticks = False)

### added
plot_function_diff(diff_algos, keys_sorted_added, added, sizes_sorted_alternating, MCU, "added_diff_samd21_alternating.pdf", "../plots/", False, zoom = True, ticks = False)

### deleted
plot_function_diff(diff_algos, keys_sorted_deleted, deleted, sizes_sorted_alternating, MCU, "deleted_diff_samd21_alternating.pdf", "../plots/", False, zoom = True, ticks = False)

### deleted
plot_function_diff(diff_algos, keys_sorted_size, size, sizes_sorted_alternating, MCU, "size_diff_samd21_alternating.pdf", "../plots/", False, zoom = True, ticks = False)


print("Done!")
