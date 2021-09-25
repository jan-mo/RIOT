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

    fig_samd20, ax_samd20 = plot_bar(array_all, xlabels, diff_algos, fig_name, width = width)
    fig_norm20, ax_norm20 = plot_bar(norm_all, xlabels, diff_algos, fig_name + " (normalized)", "size of difference / target size", width = width)

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
    bytes_changed_samd20 = []
    bytes_inserted_samd20 = []
    xlabels_samd20 = []

    chunks_samd21 = []
    bytes_changed_samd21 = []
    bytes_inserted_samd21 = []
    xlabels_samd21 = []

    for value in values_samd20:
        tmp = value.split("_")
        if "slot0" in tmp:
            xlabels_samd20.append("rev" + tmp[1] + "_rev" + tmp[3])
        elif "slot1" in tmp:
            xlabels_samd20.append("rev" + tmp[1] + "_rev" + tmp[3])
        else:
            xlabels_samd20.append("rev" + tmp[1] + "_rev" + tmp[2])
        chunks_samd20.append(values_samd20[value]["chunks"])
        bytes_changed_samd20.append(values_samd20[value]["changed"])
        bytes_inserted_samd20.append(values_samd20[value]["inserted"])

    for value in values_samd21:
        tmp = value.split("_")
        if "slot0" in tmp:
            xlabels_samd21.append("rev" + tmp[1] + "_rev" + tmp[3])
        elif "slot1" in tmp:
            xlabels_samd21.append("rev" + tmp[1] + "_rev" + tmp[3])
        else:
            xlabels_samd21.append("rev" + tmp[1] + "_rev" + tmp[2])
        chunks_samd21.append(values_samd21[value]["chunks"])
        bytes_changed_samd21.append(values_samd21[value]["changed"])
        bytes_inserted_samd21.append(values_samd21[value]["inserted"])

    if xlabels_samd20 != xlabels_samd21:
        print("Waring: Labels SAMD20 and SAMD21 are not equal!")
    else:
        xlabels = xlabels_samd20

    legend = ["SAMD20-xpro", "SAMD21-xpro"]
    chunks = [chunks_samd20, chunks_samd21]
    bytes_changed = [bytes_changed_samd20, bytes_changed_samd21]
    bytes_inserted = [bytes_inserted_samd20, bytes_inserted_samd21]

    fig_chunks, ax_chunks = plot_bar(chunks, xlabels, legend, fig_name + " number of chunks", ylabel="#chunks", figsize = (12,6), width = 0.2)
    fig_changed, ax_changed = plot_bar(bytes_changed, xlabels, legend, fig_name + " changed bytes", ylabel="changed Bytes", figsize = (12,6), width = 0.2)
    fig_inserted, ax_inserted = plot_bar(bytes_inserted, xlabels, legend, fig_name + " inserted bytes", ylabel="inserted Bytes", figsize = (12,6), width = 0.2)

    # save and close figures
    fig_chunks.savefig(path + "chunks_" + file)
    fig_changed.savefig(path + "changed_" + file)
    fig_inserted.savefig(path + "inserted_" + file)
    plt.close("all")
