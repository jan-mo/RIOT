#!/usr/bin/env python3.9

import os, json
from __finding_versions import database_files_riotboot
from __calc_diffs import calcDiff

# used differencing algos
diff_algos = ["diff", "bsdiff", "xdelta3", "rsync8", "rsync16", "rsync32", "detools_none", "detools_heat"]

folder = "algo_diffs_slots/"
folder_restore = "algo_diffs_slots/restore/"

# database
versions = []
files_samd20 = []
files_samd21 = []

[files_samd20, files_samd21, versions] = database_files_riotboot()

### clear algo_diffs folder ###
os.system("sudo rm -r " + folder)
os.system("mkdir " + folder)
os.system("mkdir " + folder_restore)

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

### split files in slots ###
slots0_samd20 = []
slots1_samd20 = []
slots0_samd21 = []
slots1_samd21 = []

for i in range(int(len(files_samd20)/4)):
    slots0_samd20.append(files_samd20[i*4])
    slots1_samd20.append(files_samd20[i*4+3])

for i in range(int(len(files_samd21)/4)):
    slots0_samd21.append(files_samd21[i*4])
    slots1_samd21.append(files_samd21[i*4+3])

diff = calcDiff(folder, folder_restore, diff_algos)

### getting alternating slots ###
#samd20
results_samd20 = diff.calc_diffs_slots_alternating(slots0_samd20, slots1_samd20, sizes_samd20, "samd20-xpro")

# clear patched folder
os.system("rm -r " + folder_restore + "*")

#samd21
results_samd21 = diff.calc_diffs_slots_alternating(slots0_samd21, slots1_samd21, sizes_samd21, "samd21-xpro")

# clear patched folder
os.system("rm -r " + folder_restore + "*")

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
with open("sizes_sorted_alternating_slots.save", 'w') as out:
    json.dump(sizes_sorted, out)

### saving versions ###
with open("versions.save", 'w') as out:
    json.dump(versions, out)



### getting every second slot ###
#samd20
results_samd20 = diff.calc_diffs_slots_same(slots0_samd20, slots1_samd20, sizes_samd20, "samd20-xpro")

# clear patched folder
os.system("rm -r " + folder_restore + "*")

#samd21
results_samd21 = diff.calc_diffs_slots_same(slots0_samd21, slots1_samd21, sizes_samd21, "samd21-xpro")

# clear patched folder
os.system("rm -r " + folder_restore + "*")

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
with open("sizes_sorted_same_slots.save", 'w') as out:
    json.dump(sizes_sorted, out)

### saving versions ###
with open("versions.save", 'w') as out:
    json.dump(versions, out)

### clear data ###
os.system("rm -r " + folder_restore)
os.system("rm " + folder + "*/*/*.sh")
os.system("rm ../database/riotboot/*/*/*.bin_*")
