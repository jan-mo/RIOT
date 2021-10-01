#!/usr/bin/env python3.9

import numpy as np
import matplotlib.pyplot as plt

###
### 
###

#### simple bar plot function ####
def plot_bar(values, xlabels, legend, name_fig, ylabel="size [kB]", figsize = (18,8), width = 0.1):

    x = np.arange(len(xlabels))  # the label locations

    plt.rcParams["figure.figsize"] = figsize

    SMALL_SIZE = 10
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 13

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # font-size of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # font-size of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # font-size of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # font-size of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend font-size
    plt.rc('figure', titlesize=BIGGER_SIZE)  # font-size of the figure title

    fig, ax = plt.subplots()

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

#### simple line plot function ####
def plot_line(values, xlabels, legend, name_fig, ylabel="size [kB]", figsize = (18,8)):

    plt.rcParams["figure.figsize"] = figsize

    SMALL_SIZE = 10
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 13

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # font-size of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # font-size of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # font-size of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # font-size of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend font-size
    plt.rc('figure', titlesize=BIGGER_SIZE)  # font-size of the figure title

    fig, ax = plt.subplots()

    for i, value in enumerate(values):
        plt.plot(xlabels, value, "o--", label = legend[i])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_title(name_fig)
    x = np.arange(len(xlabels))  # the label locations
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation='vertical')
    ax.legend()

    fig.tight_layout()

    return fig, ax

### simple plot of heatmap ####
def plot_heatmap(values, xlabels, legend, name_fig, ylabel="size [kB]", figsize = (18,8)):

    plt.rcParams["figure.figsize"] = figsize

    SMALL_SIZE = 10
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 13

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # font-size of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # font-size of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # font-size of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # font-size of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend font-size
    plt.rc('figure', titlesize=BIGGER_SIZE)  # font-size of the figure title

    fig, ax = plt.subplots()
    im = ax.imshow(values)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(xlabels)))
    ax.set_yticks(np.arange(len(legend)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(legend)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(legend)):
        for j in range(len(xlabels)):
            text = ax.text(j, i, str(values[i][j]),
                           ha="center", va="center", color="b")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    #ax.set_ylabel(ylabel)
    ax.set_title(name_fig)
    #x = np.arange(len(xlabels))  # the label locations
    #ax.set_xticks(x)
    #ax.set_xticklabels(xlabels, rotation='vertical')
    #ax.legend()

    fig.tight_layout()

    return fig, ax


### plots the differences from given keys ###
def plot_function_diff(diff_algos, keys, xlabels, values, MCU, file, path, fig_name, width = 0.1):
    array_all = []
    norm_all = []
    for algo in diff_algos:
        array = []
        norm = []
        for key in keys[algo]:
            array.append(values[MCU][algo][key]["size"]/1024)   # convert to kB
            norm.append(values[MCU][algo][key]["normalized"])   # normalizing data
            if values[MCU][algo][key]["check"] != "pass":
                name = "SAMD20 " if MCU == "samd20-xpro" else "SAMD21 "
                print("Warning: " + name + algo + " " + key + " check FAILED")
        array_all.append(array)
        norm_all.append(norm)

    fig_samd20, ax_samd20 = plot_line(array_all, xlabels, diff_algos, fig_name)
    fig_norm20, ax_norm20 = plot_line(norm_all, xlabels, diff_algos, fig_name + " (normalized)", "size of difference / target size")

    # save and close figures
    fig_samd20.savefig(path + file)
    fig_norm20.savefig(path + "norm_" + file)
    plt.close("all")

### plots the relative differences ###
def plot_function_diff_relative(diff_algos, keys, xlabels, values, file, path, fig_name, width = 0.1):
    array_all = []
    norm_all = []
    for algo in diff_algos:
        array = []
        norm = []
        for key in keys[algo]:
            array.append(values["samd21-xpro"][algo][key]["size"] - values["samd20-xpro"][algo][key]["size"])   # in Bytes
            norm.append(values["samd21-xpro"][algo][key]["normalized"] - values["samd20-xpro"][algo][key]["normalized"])   # normalizing data
            if values["samd21-xpro"][algo][key]["check"] != "pass":
                print("Warning: SAMD21 " + algo + " " + key + " check FAILED")
        array_all.append(array)
        norm_all.append(norm)

    fig_samd20, ax_samd20 = plot_bar(array_all, xlabels, diff_algos, fig_name, "size [Byte]", width = width)
    fig_norm20, ax_norm20 = plot_bar(norm_all, xlabels, diff_algos, fig_name + " (normalized)", "size of difference / target size", width = width)

    # save and close figures
    fig_samd20.savefig(path + file)
    fig_norm20.savefig(path + "norm_" + file)
    plt.close("all")


# plots chunks, bytes_changed and bytes_inserted
# values must include chunks, changed and inserted
def plot_function_matches(values_samd20, values_samd21, fig_name, file, path):

    chunks_samd20 = []
    bytes_deleted_samd20 = []
    bytes_added_samd20 = []
    xlabels_samd20 = []

    chunks_samd21 = []
    bytes_deleted_samd21 = []
    bytes_added_samd21 = []
    xlabels_samd21 = []

    ### SAMD20
    for value in values_samd20:
        tmp = value.split("_")
        if "slot0" in tmp:
            xlabels_samd20.append("rev" + tmp[1] + "_rev" + tmp[3])
        elif "slot1" in tmp:
            xlabels_samd20.append("rev" + tmp[1] + "_rev" + tmp[3])
        else:
            xlabels_samd20.append("rev" + tmp[1] + "_rev" + tmp[2])
        chunks_samd20.append(values_samd20[value]["chunks"])
        bytes_deleted_samd20.append(values_samd20[value]["deleted"])
        bytes_added_samd20.append(values_samd20[value]["added"])

    ### SAMD21
    for value in values_samd21:
        tmp = value.split("_")
        if "slot0" in tmp:
            xlabels_samd21.append("rev" + tmp[1] + "_rev" + tmp[3])
        elif "slot1" in tmp:
            xlabels_samd21.append("rev" + tmp[1] + "_rev" + tmp[3])
        else:
            xlabels_samd21.append("rev" + tmp[1] + "_rev" + tmp[2])
        chunks_samd21.append(values_samd21[value]["chunks"])
        bytes_deleted_samd21.append(values_samd21[value]["deleted"])
        bytes_added_samd21.append(values_samd21[value]["added"])

    if xlabels_samd20 != xlabels_samd21:
        print("Waring: Labels SAMD20 and SAMD21 are not equal!")
    else:
        xlabels = xlabels_samd20

    legend = ["SAMD20-xpro", "SAMD21-xpro"]
    chunks = [chunks_samd20, chunks_samd21]
    bytes_deleted = [bytes_deleted_samd20, bytes_deleted_samd21]
    bytes_added = [bytes_added_samd20, bytes_added_samd21]

    fig_chunks, ax_chunks = plot_bar(chunks, xlabels, legend, fig_name + " number of chunks", ylabel="#chunks", figsize = (12,6), width = 0.2)
    fig_changed, ax_changed = plot_bar(bytes_deleted, xlabels, legend, fig_name + " deleted bytes", ylabel="deleted Bytes", figsize = (12,6), width = 0.2)
    fig_inserted, ax_inserted = plot_bar(bytes_added, xlabels, legend, fig_name + " added bytes", ylabel="added Bytes", figsize = (12,6), width = 0.2)

    # save and close figures
    fig_chunks.savefig(path + "chunks_" + file)
    fig_changed.savefig(path + "deleted_" + file)
    fig_inserted.savefig(path + "added_" + file)
    plt.close("all")
