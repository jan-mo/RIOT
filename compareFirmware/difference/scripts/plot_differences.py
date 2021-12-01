#!/usr/bin/env python3.9

import json, os, math

from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_bar, plot_function_diff, plot_function_diff_relative

###
### script plots all differences in revisions
### the plots are stored in 'plots/'
### calculates difference between one revision and all other plots
### calculates diagonal of revisions and also SAMD20 relative to SAMD21
###

# used differencing algos
diff_algos = ["byte_diff", "rsync8", "rsync16", "rsync32", "bsdiff", "vcdiff",  "zdelta", "xdelta3", "detools_heat", "deltagen"]

plot_diagonal = True # compare diff and byte_diff

### load data ###
with open("../output/sizes_sorted.save", 'r') as json_file:
    sizes_sorted = json.load(json_file)
with open("../output/versions.save", 'r') as file:
    versions = json.load(file)

if "deltagen" in diff_algos:
    ### load deltagen data ###
    with open("../deltagen_diff/sizes_sorted.save", 'r') as json_file:
        sizes_sorted_deltagen = json.load(json_file)

    ### combine the data ###
    if len(sizes_sorted_deltagen["samd20-xpro"]["deltagen"].keys()) == len(sizes_sorted["samd20-xpro"][diff_algos[0]].keys()):
        sizes_sorted["samd20-xpro"].update(sizes_sorted_deltagen["samd20-xpro"])
        sizes_sorted["samd21-xpro"].update(sizes_sorted_deltagen["samd21-xpro"])
    else:
        print("Error: Revisions in sizes_deltagen and sizes does not match!")
        exit()


### SAMD20 bar plot ###
MCU = "samd20-xpro"
print("SAMD20")

### all
# getting keys
keys_algo = sizes_sorted[MCU][diff_algos[0]]
num_revs = int(math.sqrt(len(keys_algo)))


# setting labels and key for all algos
labels = []
for key in keys_algo:
    tmp = key.split("_")
    labels.append(tmp[-4] + tmp[-3] + "_" + tmp[-2] + tmp[-1])

keys = dict()
for algo in diff_algos:
    keys[algo] = sizes_sorted[MCU][algo].keys()

plot_function_diff(diff_algos, keys, labels, sizes_sorted, MCU, "diffalgos_samd20_all.pdf", "../plots/", "SAMD20-xpro Differencing Algorithms", figsize = (10,6), zoom = True)

### plot single rev against others
# setting labels and key for all algos
for rev in range(num_revs):
    label = labels[rev*num_revs:rev*num_revs+num_revs]

    keys = dict()
    for algo in diff_algos:
        revs = list(sizes_sorted[MCU][algo].keys())
        keys[algo] = revs[rev*num_revs:rev*num_revs+num_revs]

    plot_function_diff(diff_algos, keys, label, sizes_sorted, MCU, "diffalgos_samd20_rev_" + str(rev).zfill(2) + ".pdf", "../plots/all_revs/", "SAMD20-xpro Differencing Algorithms Revision " + str(rev).zfill(2), figsize = (10,6), zoom = True)

# plot diagonal
# setting labels and key for all algos
labels = []
names = []
for num in range(num_revs-1):
    names.append("rev_" + str(num).zfill(2) + "_rev_" + str(num+1).zfill(2))
    labels.append("rev" + str(num).zfill(2) + "_rev" + str(num+1).zfill(2))

keys = dict()
for algo in diff_algos:
    key = []
    for name in names:
        key.append(algo + "_" + name)
    keys[algo] = key

plot_function_diff(diff_algos, keys, labels, sizes_sorted, MCU, "diffalgos_samd20_diagonal.pdf", "../plots/", "SAMD20-xpro Differencing Algorithms diagonal", figsize = (10,6), width = 0.08, zoom = True)

# plot diagonal for diff and byte_diff
algos_here = ["byte_diff", "diff"]
if plot_diagonal:
    # setting labels and key for all algos
    labels = []
    names = []
    for num in range(num_revs-1):
        names.append("rev_" + str(num).zfill(2) + "_rev_" + str(num+1).zfill(2))
        labels.append("rev" + str(num).zfill(2) + "_rev" + str(num+1).zfill(2))

    keys = dict()
    for algo in algos_here:
        key = []
        for name in names:
            key.append(algo + "_" + name)
        keys[algo] = key

    plot_function_diff(algos_here, keys, labels, sizes_sorted, MCU, "diffalgos_samd20_diagonal_of_diffs.pdf", "../plots/", "SAMD20-xpro Differencing Algorithms diagonal of diff and byte_diff", figsize = (10,6), width = 0.08, zoom = False)


### SAMD21 relative bar plot ###
MCU = "samd21-xpro"
print("SAMD21")

### all
# getting keys
keys_algo = sizes_sorted[MCU][diff_algos[0]]
num_revs = int(math.sqrt(len(keys_algo)))


# setting labels and key for all algos
labels = []
for key in keys_algo:
    tmp = key.split("_")
    labels.append(tmp[-4] + tmp[-3] + "_" + tmp[-2] + tmp[-1])

keys = dict()
for algo in diff_algos:
    keys[algo] = sizes_sorted[MCU][algo].keys()

plot_function_diff_relative(diff_algos, keys, labels, sizes_sorted, "diffalgos_samd21_relative_all.pdf", "../plots/", "SAMD21-xpro Differencing Algorithms relative to SAMD20-xpro")

# plot single rev_xx
# setting labels and key for all algos
for rev in range(num_revs):
    label = labels[rev*num_revs:rev*num_revs+num_revs]

    keys = dict()
    for algo in diff_algos:
        revs = list(sizes_sorted[MCU][algo].keys())
        keys[algo] = revs[rev*num_revs:rev*num_revs+num_revs]

    plot_function_diff_relative(diff_algos, keys, label, sizes_sorted, "diffalgos_samd21_relative_rev_" + str(rev).zfill(2) + ".pdf", "../plots/all_revs/", "SAMD21-xpro Differencing Algorithms relative to SAMD20-xpro Revision " + str(rev).zfill(2))

# plot diagonal
# setting labels and key for all algos
labels = []
names = []
for num in range(num_revs-1):
    names.append("rev_" + str(num).zfill(2) + "_rev_" + str(num+1).zfill(2))
    labels.append("rev" + str(num).zfill(2) + "_rev" + str(num+1).zfill(2))

keys = dict()
for algo in diff_algos:
    key = []
    for name in names:
        key.append(algo + "_" + name)
    keys[algo] = key

plot_function_diff(diff_algos, keys, labels, sizes_sorted, MCU, "diffalgos_samd21_diagonal.pdf", "../plots/", "SAMD21-xpro Differencing Algorithms diagonal", figsize = (10,6), zoom = True)
plot_function_diff_relative(diff_algos, keys, labels, sizes_sorted, "diffalgos_samd21_diagonal_relative.pdf", "../plots/", "SAMD21-xpro Differencing Algorithms relative to SAMD20-xpro diagonal")

# plot diagonal for diff and byte_diff
algos_here = ["byte_diff", "diff"]
if plot_diagonal:
    # setting labels and key for all algos
    labels = []
    names = []
    for num in range(num_revs-1):
        names.append("rev_" + str(num).zfill(2) + "_rev_" + str(num+1).zfill(2))
        labels.append("rev" + str(num).zfill(2) + "_rev" + str(num+1).zfill(2))

    keys = dict()
    for algo in algos_here:
        key = []
        for name in names:
            key.append(algo + "_" + name)
        keys[algo] = key

    plot_function_diff(algos_here, keys, labels, sizes_sorted, MCU, "diffalgos_samd21_diagonal_of_diffs.pdf", "../plots/", "SAMD21-xpro Differencing Algorithms diagonal of diff and byte_diff", figsize = (10,6), width = 0.08, zoom = False)


### bar plot code differences ###
# calculating diff sizes
diff = []
for version in versions:
    if "rev_00" == version:
        continue
    folder = "../../data_basis/" + version
    if os.path.isfile(folder + "/previous.diff"):
        diff.append(os.path.getsize(folder + "/previous.diff"))
    else:
        # creating diff from split
        os.system("cd " + folder + " && cat previous.diff_* > previous.diff")
        diff.append(os.path.getsize(folder + "/previous.diff"))
        os.system("cd " + folder + " && rm previous.diff")

log_diff = []
versions_diff = []
for i, elem in enumerate(diff):
    value = round(elem/1024, 2)
    print("UNIX code-diff between rev_" + str(i).zfill(2) + " and rev_" + str(i+1).zfill(2) + ": " + str(value) + "kB")
    log_diff.append(math.log10(abs(elem)))
    versions_diff.append("rev" + str(i).zfill(2) + "_rev" + str(i+1).zfill(2))

fig_codediff, ax_codediff = plot_bar([log_diff], versions_diff, ["C-code UNIX diff"], "Difference between serial Revisions", "size of difference [$log_{10}$ Byte]", figsize = (10,6), width = 0.4)

### save and close figures ###
fig_codediff.savefig("../plots/code_diff.pdf")
