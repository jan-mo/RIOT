#!/usr/bin/env python3.9

import numpy as np
import matplotlib.pyplot as plt

#### bar plot function ####
def plot_bar(values, xlabels, legend, name_fig, ylabel="size [kB]", figsize = (18,8), width = 0.1):

    x = np.arange(len(xlabels))  # the label locations

    plt.rcParams["figure.figsize"] = figsize

    SMALL_SIZE = 10
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 13

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

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


def plot_function(diff_algos, keys, labels, values, MCU, file, path, fig_name):
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

    fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, fig_name)
    fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, fig_name + " (normalized)", "size of difference / target size")

    # save and close figures
    fig_samd20.savefig(path + file)
    fig_norm20.savefig(path + "norm_" + file)
    plt.close("all")


def plot_function_relative(diff_algos, keys, labels, values, file, path, fig_name):
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

    fig_samd20, ax_samd20 = plot_bar(array_all, labels, diff_algos, fig_name, "size [Byte]")
    fig_norm20, ax_norm20 = plot_bar(norm_all, labels, diff_algos, fig_name + " (normalized)", "size of difference / target size")

    # save and close figures
    fig_samd20.savefig(path + file)
    fig_norm20.savefig(path + "norm_" + file)
    plt.close("all")
