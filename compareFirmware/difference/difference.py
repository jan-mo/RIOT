#!/usr/bin/env python3.9

import os, sys, json
from shutil import move, copyfile
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import numpy as np

###
### calculates differences in firmware-database
###

# used differencing algos
diff_algos = ["diff", "bsdiff", "xdelta3", "rsync8", "rsync16", "rsync32"] # bdelta - not implemented right

database = os.listdir('../database')
versions = []
files_samd20 = []
files_samd21 = []

# create path for samd20 and samd21
for version in database:
    if os.path.isdir(os.path.join('../database/' + version)):
        # exclude suit_updater
        if version == "suit_updater":
            continue;

        versions.append(version)
        files_samd20.append('../database/' + version + '/samd20-xpro/' + version + '.bin')
        files_samd21.append('../database/' + version + '/samd21-xpro/' + version + '.bin')

files_samd20 = sorted(files_samd20)
files_samd21 = sorted(files_samd21)

folder = "algo_diffs/"
folder_patch = "algo_diffs/patched/"

# calculate all differences
def second_loop(i, file1, sizes, files, name_arch):
    for j, file2 in enumerate(files):

        #### diff ####
        if "diff" in diff_algos:
            name_diff = "diff_rev" + str(i) + "_rev" + str(j)
            folder_diff = folder + "diff/" + name_arch + "/" + name_diff
            # diff file
            os.system("diff -a " + file1 + " " + file2 + " > " + folder_diff)
            # patch file
            os.system("cp " + file1 + " " + folder_patch + name_diff)
            os.system("patch --quiet " + folder_patch + name_diff + " " + folder_diff)

        #### bsdiff ####
        if "bsdiff" in diff_algos:
            name_bsdiff = "bsdiff_rev" + str(i) + "_rev" + str(j)
            folder_bsdiff = folder + "bsdiff/" + name_arch + "/" + name_bsdiff
            # diff file
            os.system("bsdiff " + file1 + " " + file2 + " " + folder_bsdiff)
            # patch file
            os.system("bspatch " + file1 + " " + folder_patch + name_bsdiff + " " + folder_bsdiff)

        #### xdelta3 ####
        if "xdelta3" in diff_algos:
            name_xdelta3 = "xdelta3_rev" + str(i) + "_rev" + str(j)
            folder_xdelta3 = folder + "xdelta3/" + name_arch + "/" + name_xdelta3
            # diff file
            os.system("xdelta3 -e -s " + file1 + " " + file2 + " " + folder_xdelta3)
            # patch file
            os.system("xdelta3 -d -s " + file1 + " " + folder_xdelta3 + " " + folder_patch + name_xdelta3)

        #### bdelta ####
        if "bdelta" in diff_algos:
            name_bdelta = "bdelta_rev" + str(i) + "_rev" + str(j)
            folder_bdelta = folder + "bdelta/" + name_arch + "/" + name_bdelta
            # diff file
            print("bdelta " + file1 + " " + file2 + " " + folder_bdelta)
            os.system("bdelta " + file1 + " " + file2 + " " + folder_bdelta)
            # patch file
            print("bpatch " + file1 + " " + folder_patch + name_bdelta + " " + folder_bdelta)
            os.system("bpatch " + file1 + " " + folder_patch + name_bdelta + " " + folder_bdelta)

        #### rsync8 ####
        if "rsync8" in diff_algos:
            name_rsync8 = "rsync8_rev" + str(i) + "_rev" + str(j)
            folder_rsync8 = folder + "rsync8/" + name_arch + "/" + name_rsync8
            rsync8_par = "_rsync8_" + str(i) + str(j)     # save file for parallel loop
            # diff file
            os.system("cp " + file1 + " " + file1 + rsync8_par)
            os.system("cp " + file2 + " " + file2 + rsync8_par)
            os.system("rsync -arvq -B=8 --only-write-batch=" + folder_rsync8 + " " + file2 + rsync8_par + " " + file1 + rsync8_par)
            # patch file
            os.system("rsync -arvq -B=8 --read-batch=" + folder_rsync8 + " " + file1 + rsync8_par)
            os.system("cp " + file1 + rsync8_par + " " + folder_patch + name_rsync8)

        #### rsync16 ####
        if "rsync16" in diff_algos:
            name_rsync16 = "rsync16_rev" + str(i) + "_rev" + str(j)
            folder_rsync16 = folder + "rsync16/" + name_arch + "/" + name_rsync16
            rsync16_par = "_rsync16_" + str(i) + str(j)     # save file for parallel loop
            # diff file
            os.system("cp " + file1 + " " + file1 + rsync16_par)
            os.system("cp " + file2 + " " + file2 + rsync16_par)
            os.system("rsync -arvq -B=16 --only-write-batch=" + folder_rsync16 + " " + file2 + rsync16_par + " " + file1 + rsync16_par)
            # patch file
            os.system("rsync -arvq -B=16 --read-batch=" + folder_rsync16 + " " + file1 + rsync16_par)
            os.system("cp " + file1 + rsync16_par + " " + folder_patch + name_rsync16)

        #### rsync32 ####
        if "rsync32" in diff_algos:
            name_rsync32 = "rsync32_rev" + str(i) + "_rev" + str(j)
            folder_rsync32 = folder + "rsync32/" + name_arch + "/" + name_rsync32
            rsync32_par = "_rsync32_" + str(i) + str(j)     # save file for parallel loop
            # diff file
            os.system("cp " + file1 + " " + file1 + rsync32_par)
            os.system("cp " + file2 + " " + file2 + rsync32_par)
            os.system("rsync -arvq -B=32 --only-write-batch=" + folder_rsync32 + " " + file2 + rsync32_par + " " + file1 + rsync32_par)
            # patch file
            os.system("rsync -arvq -B=32 --read-batch=" + folder_rsync32 + " " + file1 + rsync32_par)
            os.system("cp " + file1 + rsync32_par + " " + folder_patch + name_rsync32)



        #### check patch and calc sizes ####
        if "diff" in diff_algos:
            sizes["diff"][name_diff] = {"size":os.path.getsize(folder_diff),
                                        "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_diff) else "fail"}
        
        if "bsdiff" in diff_algos:
            sizes["bsdiff"][name_bsdiff] = {"size":os.path.getsize(folder_bsdiff),
                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_bsdiff) else "fail"}

        if "xdelta3" in diff_algos:
            sizes["xdelta3"][name_xdelta3] = {"size":os.path.getsize(folder_xdelta3),
                                              "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_xdelta3) else "fail"}

        if "bdelta" in diff_algos:
            sizes["bdelta"][name_bdelta] = os.path.getsize(folder + name_bdelta)

        if "rsync8" in diff_algos:
            sizes["rsync8"][name_rsync8] = {"size":os.path.getsize(folder_rsync8),
                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_rsync8) else "fail"}

        if "rsync16" in diff_algos:        
            sizes["rsync16"][name_rsync16] = {"size":os.path.getsize(folder_rsync16),
                                              "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_rsync16) else "fail"}

        if "rsync32" in diff_algos:        
            sizes["rsync32"][name_rsync32] = {"size":os.path.getsize(folder_rsync32),
                                              "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_rsync32) else "fail"}

    return sizes

# clear folder differences
os.system("rm -r " + folder + "*")

# create algo folders
os.system("mkdir " + folder_patch)
for algo in diff_algos:
    os.system("mkdir " + folder + algo)
    os.system("mkdir " + folder + algo + "/samd20-xpro/")
    os.system("mkdir " + folder + algo + "/samd21-xpro/")

# create dictionary
sizes_all = dict()
for algo in diff_algos:
    sizes_all[algo] = dict()

### samd20-xpro ###
results_samd20 = Parallel(n_jobs=-1)(delayed(second_loop)(i, file1, sizes_all, files_samd20, "samd20-xpro") for i, file1 in enumerate(files_samd20))

# clear patched folder
os.system("rm -r " + folder_patch + "*")

### samd21-xpro ###
results_samd21 = Parallel(n_jobs=-1)(delayed(second_loop)(i, file1, sizes_all, files_samd21, "samd21-xpro") for i, file1 in enumerate(files_samd21))

# clear database
for file in files_samd20:
    os.system("rm " + file + "_*")
for file in files_samd21:
    os.system("rm " + file + "_*")

### clear data ###
os.system("rm -r " + folder_patch)
for algo in diff_algos:
    os.system("rm -r " + folder + algo + "/samd20-xpro/" + "*.sh")
    os.system("rm -r " + folder + algo + "/samd21-xpro/" + "*.sh")


### build one dict ###
sizes_all_arch = dict()
sizes_all_arch["samd20-xpro"] = sizes_all
sizes_all_arch["samd21-xpro"] = sizes_all

# add dict samd20
for elem in results_samd20:
    for algo in diff_algos:
        for key in elem[algo].keys():
            sizes_all_arch["samd20-xpro"][algo][key] = elem[algo][key]

# add dict samd21
for elem in results_samd21:
    for algo in diff_algos:
        for key in elem[algo].keys():
            sizes_all_arch["samd21-xpro"][algo][key] = elem[algo][key]



# show graph of differences
# samd20
labels_1 = []
revs = sizes_all_arch["samd20-xpro"]["diff"].keys()
for elem in revs:
    labels_1.append(elem[5:])

array_all = []
for algo in diff_algos:
    revs = sizes_all_arch["samd20-xpro"][algo].keys()
    array = []
    for rev in revs:
        array.append(sizes_all_arch["samd20-xpro"][algo][rev]["size"])
    array_all.append(array)

diff_1 = array_all[0]
bsdiff_1 = array_all[1]
xdelta3_1 = array_all[2]
rsync8_1 = array_all[3]
rsync16_1 = array_all[4]
rsync32_1 = array_all[5]


x = np.arange(len(labels_1))  # the label locations

fig1, ax1 = plt.subplots()
rects1_1 = ax1.bar(x - 0.3, diff_1, 0.15, label='diff')
rects2_1 = ax1.bar(x - 0.2, bsdiff_1, 0.15, label='bsdiff')
rects3_1 = ax1.bar(x - 0.1, xdelta3_1, 0.15, label='xdelta3')
rects4_1 = ax1.bar(x + 0.1, rsync8_1, 0.15, label='rsync8')
rects5_1 = ax1.bar(x + 0.2, rsync16_1, 0.15, label='rsync16')
rects6_1 = ax1.bar(x + 0.3, rsync32_1, 0.15, label='rsync32')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax1.set_ylabel('size [kB]')
ax1.set_title('SAMD20-xpro diff size')
ax1.set_xticks(x)
ax1.set_xticklabels(labels_1, rotation='vertical')
ax1.legend()

fig1.tight_layout()



#### samd21
labels_2 = []
revs = sizes_all_arch["samd21-xpro"]["diff"].keys()
for elem in revs:
    labels_2.append(elem[5:])

array_all = []
for algo in diff_algos:
    revs = sizes_all_arch["samd21-xpro"][algo].keys()
    array = []
    for rev in revs:
        array.append(sizes_all_arch["samd21-xpro"][algo][rev]["size"])
    array_all.append(array)

diff_2 = array_all[0]
bsdiff_2 = array_all[1]
xdelta3_2 = array_all[2]
rsync8_2 = array_all[3]
rsync16_2 = array_all[4]
rsync32_2 = array_all[5]


x = np.arange(len(labels_2))  # the label locations

fig2, ax2 = plt.subplots()
rects1 = ax2.bar(x - 0.3, diff_2, 0.15, label='diff')
rects2 = ax2.bar(x - 0.2, bsdiff_2, 0.15, label='bsdiff')
rects3 = ax2.bar(x - 0.1, xdelta3_2, 0.15, label='xdelta3')
rects4 = ax2.bar(x + 0.1, rsync8_2, 0.15, label='rsync8')
rects5 = ax2.bar(x + 0.2, rsync16_2, 0.15, label='rsync16')
rects6 = ax2.bar(x + 0.3, rsync32_2, 0.15, label='rsync32')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax2.set_ylabel('size [kB]')
ax2.set_title('SAMD21-xpro diff size')
ax2.set_xticks(x)
ax2.set_xticklabels(labels_2, rotation='vertical')
ax2.legend()

fig2.tight_layout()

plt.show()


#print(json.dumps(sizes_all_arch, indent = 4))
