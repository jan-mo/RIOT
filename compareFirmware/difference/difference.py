#!/usr/bin/env python3.9

import os, sys, json, distro
from shutil import move, copyfile
# parallel processing
from pathos.multiprocessing import ProcessingPool as Pool
from pathos.helpers import mp as helper

###
### calculates differences in firmware-database
###

# used differencing algos
diff_algos = ["diff", "bsdiff", "xdelta3", "rsync8", "rsync16", "rsync32"] # bdelta - not implemented right
pkg_arch = ["diffutils bsdiff xdelta3 rsync"]
pkg_ubuntu = ["diffutils bsdiff xdelta3 rsync"]

# database
database = os.listdir('../database')
versions = []
files_samd20 = []
files_samd21 = []

### searching path for samd20 and samd21 ###
for version in database:
    if os.path.isdir(os.path.join('../database/' + version)):
        # exclude suit_updater
        if version == "suit_updater":
            continue;

        # collection all versions
        versions.append(version)
        files_samd20.append('../database/' + version + '/samd20-xpro/' + version + '.bin')
        files_samd21.append('../database/' + version + '/samd21-xpro/' + version + '.bin')

        # remove old files
        os.system("rm -rf ../database/" + version + '/samd20-xpro/' + version + '.bin_*')
        os.system("rm -rf ../database/" + version + '/samd21-xpro/' + version + '.bin_*')

files_samd20 = sorted(files_samd20)
files_samd21 = sorted(files_samd21)
versions = sorted(versions)

folder = "algo_diffs/"
folder_patch = "algo_diffs/patched/"

### clear algo_diffs folder ###
os.system("sudo rm -r " + folder)
os.system("mkdir " + folder)
os.system("mkdir " + folder_patch)

### calculate all differences ###
def second_loop(i, file1, files, sizes, name_arch):
    # getting PID
    pid = helper.current_process().pid
    print(name_arch + " differences of Rev_" + str(i) + " PID:" + str(pid))

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
            rsync8_par = "_rsync8_" + str(pid)      # save file for parallel loop
            # diff file
            os.system("cp " + file1 + " " + file1 + rsync8_par)
            if i != j :
                os.system("cp " + file2 + " " + file2 + rsync8_par)
            os.system("rsync -arvq -B=8 --only-write-batch=" + folder_rsync8 + " " + file2 + rsync8_par + " " + file1 + rsync8_par)
            # patch file
            os.system("rsync -arvq -B=8 --read-batch=" + folder_rsync8 + " " + file1 + rsync8_par)
            os.system("mv " + file1 + rsync8_par + " " + folder_patch + name_rsync8)
            if i != j:
                os.system("rm " + file2 + rsync8_par)

        #### rsync16 ####
        if "rsync16" in diff_algos:
            name_rsync16 = "rsync16_rev" + str(i) + "_rev" + str(j)
            folder_rsync16 = folder + "rsync16/" + name_arch + "/" + name_rsync16
            rsync16_par = "_rsync16_" + str(pid)    # save file for parallel loop
            # diff file
            os.system("cp " + file1 + " " + file1 + rsync16_par)
            if i != j:
                os.system("cp " + file2 + " " + file2 + rsync16_par)
            os.system("rsync -arvq -B=16 --only-write-batch=" + folder_rsync16 + " " + file2 + rsync16_par + " " + file1 + rsync16_par)
            # patch file
            os.system("rsync -arvq -B=16 --read-batch=" + folder_rsync16 + " " + file1 + rsync16_par)
            os.system("mv " + file1 + rsync16_par + " " + folder_patch + name_rsync16)
            if i != j:
                os.system("rm " + file2 + rsync16_par)

        #### rsync32 ####
        if "rsync32" in diff_algos:
            name_rsync32 = "rsync32_rev" + str(i) + "_rev" + str(j)
            folder_rsync32 = folder + "rsync32/" + name_arch + "/" + name_rsync32
            rsync32_par = "_rsync32_" + str(pid)    # save file for parallel loop
            # diff file
            os.system("cp " + file1 + " " + file1 + rsync32_par)
            if i != j:
                os.system("cp " + file2 + " " + file2 + rsync32_par)
            os.system("rsync -arvq -B=32 --only-write-batch=" + folder_rsync32 + " " + file2 + rsync32_par + " " + file1 + rsync32_par)
            # patch file
            os.system("rsync -arvq -B=32 --read-batch=" + folder_rsync32 + " " + file1 + rsync32_par)
            os.system("mv " + file1 + rsync32_par + " " + folder_patch + name_rsync32)
            if i != j:
                os.system("rm " + file2 + rsync32_par)

        #### check patch and calc sizes ####
        if "diff" in diff_algos:
            sizes["diff"][name_diff] = {"size":os.path.getsize(folder_diff),
                                        "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_diff) else "fail",
                                        "normalized":os.path.getsize(folder_diff)/os.path.getsize(file2)}
        if "bsdiff" in diff_algos:
            sizes["bsdiff"][name_bsdiff] = {"size":os.path.getsize(folder_bsdiff),
                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_bsdiff) else "fail",
                                            "normalized":os.path.getsize(folder_bsdiff)/os.path.getsize(file2)}
        if "xdelta3" in diff_algos:
            sizes["xdelta3"][name_xdelta3] = {"size":os.path.getsize(folder_xdelta3),
                                              "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_xdelta3) else "fail",
                                              "normalized":os.path.getsize(folder_xdelta3)/os.path.getsize(file2)}
        if "bdelta" in diff_algos:
            sizes["bdelta"][name_bdelta] = os.path.getsize(folder + name_bdelta)
        if "rsync8" in diff_algos:
            sizes["rsync8"][name_rsync8] = {"size":os.path.getsize(folder_rsync8),
                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_rsync8) else "fail",
                                            "normalized":os.path.getsize(folder_rsync8)/os.path.getsize(file2)}
        if "rsync16" in diff_algos:        
            sizes["rsync16"][name_rsync16] = {"size":os.path.getsize(folder_rsync16),
                                              "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_rsync16) else "fail",
                                              "normalized":os.path.getsize(folder_rsync16)/os.path.getsize(file2)}
        if "rsync32" in diff_algos:        
            sizes["rsync32"][name_rsync32] = {"size":os.path.getsize(folder_rsync32),
                                              "check":"pass" if os.path.getsize(file2) == os.path.getsize(folder_patch + name_rsync32) else "fail",
                                              "normalized":os.path.getsize(folder_rsync32)/os.path.getsize(file2)}
    return [sizes]


### create algo folders ###
for algo in diff_algos:
    os.system("mkdir " + folder + algo)
    os.system("mkdir " + folder + algo + "/samd20-xpro/")
    os.system("mkdir " + folder + algo + "/samd21-xpro/")

### create dictionary ###
sizes_samd20 = dict()
sizes_samd21 = dict()
for algo in diff_algos:
    sizes_samd20[algo] = dict()
    sizes_samd21[algo] = dict()

### checking difftools installed ###
### supporting Ubuntu (apt-get) and Arch (yay)
dist = distro.linux_distribution()
if dist == "Arch Linux":
    os.system("yay -S " + pkg_arch)
elif dist == "Ubuntu":
    os.system("sudo apt-get install " + pkg_arch)

### samd20-xpro ###
num = []
file1 = []
files = []
sizes = []
arch = []
for i, file in enumerate(files_samd20):
    num.append(i)
    file1.append(file)
    files.append(files_samd20)
    sizes.append(sizes_samd20)
    arch.append("samd20-xpro")

result = Pool().amap(second_loop, num, file1, files, sizes, arch)
results_samd20 = result.get()

# clear patched folder
os.system("rm -r " + folder_patch + "*")

### samd21-xpro ###
num = []
file1 = []
files = []
sizes = []
arch = []
for i, file in enumerate(files_samd21):
    num.append(i)
    file1.append(file)
    files.append(files_samd21)
    sizes.append(sizes_samd21)
    arch.append("samd21-xpro")

result = Pool().amap(second_loop, num, file1, files, sizes, arch)
results_samd21 = result.get()

### clear data ###
os.system("rm -r " + folder_patch)
os.system("rm " + folder + "rsync8/" + "samd20-xpro" + "/*.sh")
os.system("rm " + folder + "rsync16/" + "samd20-xpro" + "/*.sh")
os.system("rm " + folder + "rsync32/" + "samd20-xpro" + "/*.sh")
os.system("rm " + folder + "rsync8/" + "samd21-xpro" + "/*.sh")
os.system("rm " + folder + "rsync16/" + "samd21-xpro" + "/*.sh")
os.system("rm " + folder + "rsync32/" + "samd21-xpro" + "/*.sh")

### build one dict ###
sizes_all_arch = dict()
sizes_all_arch["samd20-xpro"] = dict()
sizes_all_arch["samd21-xpro"] = dict()
for algo in diff_algos:
    sizes_all_arch["samd20-xpro"][algo] = dict()
    sizes_all_arch["samd21-xpro"][algo] = dict()

### add samd20 to dict ###
for result in results_samd20:
    for elem in result:
        for algo in diff_algos:
            for key in elem[algo].keys():
                sizes_all_arch["samd20-xpro"][algo][key] = elem[algo][key]
            

### add samd21 to dict ###
for result in results_samd21:
    for elem in result:
        for algo in diff_algos:
            for key in elem[algo].keys():
                sizes_all_arch["samd21-xpro"][algo][key] = elem[algo][key]

### sorting dict ###
sizes_sorted = dict()
sizes_sorted["samd20-xpro"] = dict()
sizes_sorted["samd21-xpro"] = dict()

for algo in diff_algos:
    sizes_sorted["samd20-xpro"][algo] = dict()
    sizes_sorted["samd21-xpro"][algo] = dict()
    for i in sorted(sizes_all_arch["samd20-xpro"][algo]):
        sizes_sorted["samd20-xpro"][algo][i] = sizes_all_arch["samd20-xpro"][algo][i]
    for i in sorted(sizes_all_arch["samd21-xpro"][algo]):
        sizes_sorted["samd21-xpro"][algo][i] = sizes_all_arch["samd21-xpro"][algo][i]

### saving to JSON-file ###
with open("sizes_sorted.save", 'w') as out:
    json.dump(sizes_sorted, out)

### saving versions ###
with open("versions.save", 'w') as out:
    json.dump(versions, out)
