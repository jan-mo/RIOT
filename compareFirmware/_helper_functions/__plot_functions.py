#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme()
import pandas as pd
from numpy import mean as estimate

###
### 
###

#### simple bar plot function ####
def plot_bar(values, xlabels, legend, name_fig=False, ylabel="size [kB]", figsize = (18,8), width = 0.1):

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
    if name_fig != False:
        ax.set_title(name_fig)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=45)
    ax.legend(ncol=3, loc = 'upper right')

    fig.tight_layout()

    return fig, ax

#### simple line plot function ####
def plot_line(values, xlabels, legend, name_fig=False, ylabel="size [kB]", figsize = (18, 8), zoom = True, ticks = True):

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

    line_style = ["o-", "x-", "x-.", "x--", "s-", "s-.", "v-", "v-.", ".-", ".-.", ".--", "-", "-.", "--"]

    for i, value in enumerate(values):
        if legend[i] == "baseline":
            label = "baseline"
            line = 2.5
            line_style[i] = "--"
        else:
            label = legend[i]
            line = 1

        plt.plot(xlabels, value, line_style[i], label = label, linewidth = line)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    if name_fig != False:
        ax.set_title(name_fig)
    if ticks:
        x = np.arange(len(xlabels))  # the label locations
        ax.set_xticks(x)
        ax.set_xticklabels(xlabels, rotation=45)
    else:
        x = np.arange(0,xlabels[-1],int(xlabels[-1]/10))  # the label locations
        ax.set_xticks(x)
        ax.set_xticklabels(x, rotation=45)

    ax.legend(ncol=3, loc = 'upper center')

    # zoom y axis
    if zoom:
        plt.ylim(-0.025, 1.025);

    fig.tight_layout()

    return fig, ax

def __convert_name_to_json_string(name):
    if name == "bzip2":
        return "bz2"
    elif name == "heatshrink":
        return "hs"
    else:
        return name

### plots a line of compression and differencing algorithm with mean and standard deviation
def plot_line_compression(data_json, def_diff_algos, def_compression, name_fig, ylabel, figsize=(10,6), zoom=False):

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

    data = pd.DataFrame()
    data["values"] = []
    data["diff_algos"] = []
    data["compression"] = []
    for diff in def_diff_algos:
        diff = __convert_name_to_json_string(diff)
        for comp in def_compression:
            comp_old = comp
            comp = __convert_name_to_json_string(comp)
            for entry in data_json[diff][comp]:
                value = data_json[diff][comp][entry]["reduction"]
                data = data.append({"values":value,"diff_algos":diff,"compression":comp_old}, ignore_index=True)

    ax = sns.boxplot(
        data = data,
        x = "diff_algos", y = "values", hue = "compression",
        #estimator = estimate
    )

    ax.set_ylabel(ylabel)

    x = np.arange(len(def_diff_algos))  # the label locations
    ax.set_xticks(x)
    ax.set_xticklabels(def_diff_algos, rotation=45)
    ax.set_xlabel(None)
    if name_fig != False:
        ax.set_title(name_fig)
    ax.legend(ncol=2)

    # zoom y axis
    if zoom:
        plt.ylim(-0.025, 1.35);

    fig.tight_layout()

    return fig, ax

### plots a bar of compression algorithms with mean and standard deviation
def plot_bar_compression(data_json, def_compression, name_fig, ylabel, figsize=(10,6), zoom=False):

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

    data = pd.DataFrame()
    data["values"] = []
    data["compression"] = []
    data["revisions"] = []
    for comp in def_compression:
        comp = __convert_name_to_json_string(comp)
        for entry in data_json[comp]:
            value = data_json[comp][entry]["reduction"]
            data = data.append({"values":value,"compression":comp, "revisions": entry}, ignore_index=True)

    ax = sns.barplot(
        data = data,
        x = "compression", y = "values",
        capsize = 0.15, estimator = estimate
    )

    ax.set_ylabel(ylabel)

    x = np.arange(len(def_compression))  # the label locations
    ax.set_xticks(x)
    ax.set_xticklabels(def_compression, rotation=45)
    ax.set_xlabel(None)
    if name_fig != False:
        ax.set_title(name_fig)

    # zoom y axis
    if zoom:
        plt.ylim(0.25, 1.05);

    fig.tight_layout()

    return fig, ax

### simple plot of heatmap ####
def plot_heatmap_matches(chunks, bytes_deleted, bytes_added, sizes_diff, xlabels, board, name_fig, ylabels, figsize = (18,8)):

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

    data = pd.DataFrame(index = ylabels)

    #zeros = []

    for i in range(len(xlabels)):
        chunks[i] = float(format(chunks[i]/100, '.4f'))
        bytes_added[i] = float(format(bytes_added[i]/1000, '.4f'))
        bytes_deleted[i] = float(format(bytes_deleted[i]/1000, '.4f'))
        sizes_diff[i] = float(format(sizes_diff[i]/10, '.4f'))
        #zeros.append(None)

    data[xlabels] = [chunks, bytes_added, bytes_deleted, sizes_diff]

    fig, ax = plt.subplots()
    ax = sns.heatmap(data, annot = True, vmin = 0, vmax = 50, lw = 0.1, cbar = False)
    ax.set_yticklabels(ylabels, rotation = 0, multialignment = "center")
    ax.set_xticklabels(xlabels, rotation = 45)
    if name_fig != False:
        ax.set_title(board + " " + name_fig)

    fig.tight_layout()

    return fig, ax


### plots the differences from given keys ###
def plot_function_diff(diff_algos, keys, xlabels, values, MCU, file, path, fig_name = False, figsize = (10,6), zoom = False, ticks = True):
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

    if fig_name != False:
        fig_samd20, ax_samd20 = plot_line(array_all, xlabels, diff_algos, fig_name, figsize = figsize, zoom = False, ticks = ticks)
        fig_norm20, ax_norm20 = plot_line(norm_all, xlabels, diff_algos, fig_name + " (normalized)", "size of difference / target size", figsize = figsize, zoom = zoom, ticks = ticks)
    else:
        fig_samd20, ax_samd20 = plot_line(array_all, xlabels, diff_algos, figsize = figsize, zoom = False, ticks = ticks)
        fig_norm20, ax_norm20 = plot_line(norm_all, xlabels, diff_algos, ylabel="size of difference / target size", figsize = figsize, zoom = zoom, ticks = ticks)

    # save and close figures
    fig_samd20.savefig(path + file)
    fig_norm20.savefig(path + "norm_" + file)

    if "slot" in file:
        print(file)
        for i, diff in enumerate(diff_algos):
            mean = np.mean(norm_all[i])
            std = np.std(norm_all[i])
            print(diff, ": ")
            print("\t mean: ", round(mean*100,2), "%")
            print("\t std: ", round(std*100,2), "%")
        print()

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

    if fig_name != False:
        fig_samd20, ax_samd20 = plot_bar(array_all, xlabels, diff_algos, fig_name, "size [Byte]", width = width)
        fig_norm20, ax_norm20 = plot_bar(norm_all, xlabels, diff_algos, fig_name + " (normalized)", "size of difference / target size", width = width)
    else:
        fig_samd20, ax_samd20 = plot_bar(array_all, xlabels, diff_algos, ylabel="size [Byte]", width = width)
        fig_norm20, ax_norm20 = plot_bar(norm_all, xlabels, diff_algos, ylabel="size of difference / target size", width = width)


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
    sizes_diff_samd20 = []
    xlabels_samd20 = []

    chunks_samd21 = []
    bytes_deleted_samd21 = []
    bytes_added_samd21 = []
    sizes_diff_samd21 = []
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
        sizes_diff_samd20.append(values_samd20[value]["size"])

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
        sizes_diff_samd21.append(values_samd21[value]["size"])

    if xlabels_samd20 != xlabels_samd21:
        print("Waring: Labels SAMD20 and SAMD21 are not equal!")
    else:
        xlabels = xlabels_samd20

    fig_samd20, ax_samd20 = plot_heatmap_matches(chunks_samd20, bytes_deleted_samd20, bytes_added_samd20, sizes_diff_samd20, xlabels, "SAMD20-xpro", fig_name, ylabels=["# chunks\n[x100]", "# added bytes\n[x1000]", "# deleted bytes\n[x1000]", "size of diff\n[x10 kB]"], figsize = (12,6))
    fig_samd21, ax_samd21 = plot_heatmap_matches(chunks_samd21, bytes_deleted_samd21, bytes_added_samd21, sizes_diff_samd21, xlabels, "SAMD21-xpro", fig_name, ylabels=["# chunks\n[x100]", "# added bytes\n[x1000]", "# deleted bytes\n[x1000]", "size of diff\n[x10 kB]"], figsize = (12,6))
    # save and close figures
    fig_samd20.savefig(path + "matches_samd20_" + file)
    fig_samd21.savefig(path + "matches_samd21_" + file)
    plt.close("all")
