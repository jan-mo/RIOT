#!/usr/bin/env python3.9

import json, os, math
import matplotlib.pyplot as plt
import numpy as np


# used differencing algos
diff_algos = [ "diff", "bsdiff", "xdelta3", "rsync8", "rsync16", "rsync32", "deltagen"] # bdelta - not implemented right

### load data ###
with open("sizes_sorted.save", 'r') as json_file:
    sizes_sorted = json.load(json_file)
with open("versions.save", 'r') as file:
    versions = json.load(file)

### load deltagen data ###
with open("deltagen_diff/sizes_sorted.save", 'r') as json_file:
    sizes_sorted_deltagen = json.load(json_file)

### combine the data ###
sizes_sorted["samd20-xpro"].update(sizes_sorted_deltagen["samd20-xpro"])
sizes_sorted["samd21-xpro"].update(sizes_sorted_deltagen["samd21-xpro"])

#### bar plot function ####
def plot_bar(values, xlabels, legend, name_fig, ylabel="size [kB]"):

    x = np.arange(len(xlabels))  # the label locations

    plt.rcParams["figure.figsize"] = (18,8)

    fig, ax = plt.subplots()

    width = 0.1
    length = len(legend)

    for i, value in enumerate(values):
        offset = x + ((i-length/2) * width + width/2) if i < length/2 else x + ((i-length/2+1) * width - width/2)
        ax.bar(offset, value, width, label=legend[i])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_title(name_fig)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation='vertical')
    ax.legend()

    fig.tight_layout()

    return fig, ax


### SAMD20 bar plot ###
labels = []
revs = sizes_sorted["samd20-xpro"][diff_algos[0]].keys()
for elem in revs:
    tmp = elem.split("_")
    labels.append("rev" + tmp[2] + "_rev" + tmp[4])

array_all = []
norm_all = []
for algo in diff_algos:
    revs = sizes_sorted["samd20-xpro"][algo].keys()
    array = []
    norm = []
    for rev in revs:
        array.append(sizes_sorted["samd20-xpro"][algo][rev]["size"]/1024)   # convert to kB
        norm.append(sizes_sorted["samd20-xpro"][algo][rev]["normalized"])   # normalizing data
        if sizes_sorted["samd20-xpro"][algo][rev]["check"] != "pass":
            print("Warning: SAMD20 " + algo + " " + rev + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, "SAMD20-xpro differencing algorithms")
fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, "SAMD20-xpro differencing algorithms (normalized)", "size reduction")

# save and close figures
fig_samd20.savefig("plots/diffalgos_samd20_all.pdf")
fig_norm20.savefig("plots/norm_diffalgos_samd20_all.pdf")
plt.close("all")

# plot single rev_xx
figures_array = []
figures_norm = []
num_revs = int(math.sqrt(len(revs)))
for rev in range(num_revs):
    label = labels[rev*num_revs:rev*num_revs+num_revs]
    array = []
    norm = []
    for algo in range(len(array_all)):
        array.append(array_all[algo][rev*num_revs:rev*num_revs+num_revs])
        norm.append(norm_all[algo][rev*num_revs:rev*num_revs+num_revs])

    fig, ax = plot_bar(array, label, diff_algos, "SAMD20-xpro differencing algorithms Revision " + str(rev).zfill(2))
    fig_norm, ax = plot_bar(norm, label, diff_algos, "SAMD20-xpro differencing algorithms Revision " + str(rev).zfill(2) + " (normalized)", "size reduction")

    ### save and close figures ###
    fig.savefig("plots/diffalgos_samd20_rev_" + str(rev).zfill(2) + ".pdf")
    fig_norm.savefig("plots/norm_diffalgos_samd20_rev_" + str(rev).zfill(2) + ".pdf")
    plt.close("all")


### SAMD21 relative bar plot ###
labels = []
revs = sizes_sorted["samd21-xpro"][diff_algos[0]].keys()
for elem in revs:
    tmp = elem.split("_")
    labels.append("rev" + tmp[2] + "_rev" + tmp[4])

array_all = []
norm_all = []
for algo in diff_algos:
    revs = sizes_sorted["samd21-xpro"][algo].keys()
    array = []
    norm = []
    for rev in revs:
        array.append(sizes_sorted["samd20-xpro"][algo][rev]["size"] - sizes_sorted["samd21-xpro"][algo][rev]["size"])   # in Bytes
        norm.append(sizes_sorted["samd20-xpro"][algo][rev]["normalized"] - sizes_sorted["samd21-xpro"][algo][rev]["normalized"])   # normalizing data
        if sizes_sorted["samd21-xpro"][algo][rev]["check"] != "pass":
            print("Warning: SAMD21 " + algo + " " + rev + " check FAILED") 
    array_all.append(array)
    norm_all.append(norm)

fig_samd21, ax_samd21 = plot_bar(array_all, labels, diff_algos, "SAMD21-xpro differencing algorithms relative to SAMD20-xpro", "size [Byte]")
fig_norm21, ax_norm21 = plot_bar(norm_all, labels, diff_algos, "SAMD21-xpro differencing algorithms relative to SAMD20-xpro (normalized)", "size reduction")

### save and close figures ###
fig_samd21.savefig("plots/diffalgos_samd21_relative_all.pdf")
fig_norm21.savefig("plots/norm_diffalgos_samd21_relative_all.pdf")
plt.close("all")


# plot single rev_xx
num_revs = int(math.sqrt(len(revs)))
for rev in range(num_revs):
    label = labels[rev*num_revs:rev*num_revs+num_revs]
    array = []
    norm = []
    for algo in range(len(array_all)):
        array.append(array_all[algo][rev*num_revs:rev*num_revs+num_revs])
        norm.append(norm_all[algo][rev*num_revs:rev*num_revs+num_revs])

    fig, ax1 = plot_bar(array, label, diff_algos, "SAMD21-xpro differencing algorithms relative to SAMD20-xpro Revision " + str(rev).zfill(2), "size [Byte]")
    fig_norm, ax2 = plot_bar(norm, label, diff_algos, "SAMD21-xpro differencing algorithms relative to SAMD20-xpro Revision " + str(rev).zfill(2) + " (normalized)", "size reduction")

    ### save and close figures ###
    fig.savefig("plots/diffalgos_samd21_relative_rev_" + str(rev).zfill(2) + ".pdf")
    fig_norm.savefig("plots/norm_diffalgos_samd21_relative_rev_" + str(rev).zfill(2) + ".pdf")
    plt.close("all")


### bar plot code differences ###
diff = []
for i, version in enumerate(versions):
    folder = "../database/" + version
    if os.path.isfile(folder + "/firmware.diff"):
        diff.append(os.path.getsize(folder + "/firmware.diff"))
        if i > 1:
            diff[i] = diff[i] - diff[i-1]
    else:
        # creating diff from split
        os.system("cd " + folder + " && cat firmware.diff_* > firmware.diff")
        diff.append(os.path.getsize(folder + "/firmware.diff")) # convert to kB
        os.system("cd " + folder + " && rm firmware.diff")
        if i > 1:
            diff[i] = diff[i] - diff[i-1]

log_diff = []
for elem in diff:
    if elem < 0.0:
        elem = -elem
    if elem != 0.0:
        log_diff.append(math.log(elem))
    else:
        log_diff.append(elem)

fig_codediff, ax_codediff = plot_bar([log_diff], versions, ["code diff"], "Difference [in kB] between revision and previous revision")

### save and close figures ###
fig_codediff.savefig("plots/code_diff.pdf")
