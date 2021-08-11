#!/usr/bin/env python3.9

import os, sys, json
from shutil import move, copyfile

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

# samd20-xpro
sizes_all = dict()
sizes_all["diff"] = dict()
sizes_all["bsdiff"] = dict()

for i, file1 in enumerate(files_samd20):
    for j, file2 in enumerate(files_samd20):
        folder = "differences/"

        #### diff ####
        name_diff = "diff_rev" + str(i) + "_rev" + str(j)
        command = "diff -a " + file1 + " " + file2 + " > " + folder + name_diff
        os.system(command)

        #### bsdiff ####
        name_bsdiff = "bsdiff_rev" + str(i) + "_rev" + str(j)
        command = "bsdiff " + file1 + " " + file2 + " " + folder + name_bsdiff
        os.system(command)

        #### calc sizes ####
        sizes_all["diff"][name_diff] = os.path.getsize(folder + name_diff)
        sizes_all["bsdiff"][name_bsdiff] = os.path.getsize(folder + name_bsdiff)

print(json.dumps(sizes_all, indent = 4))


# xdelta3


# bdelta


# zdelta