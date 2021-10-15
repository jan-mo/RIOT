#!/usr/bin/env python3.8

import os, json

database = "../../data_basis/riotboot/"
database_diff = "data_basis/riotboot/"

sizes = dict()
sizes["samd20-xpro"] = dict()
sizes["samd21-xpro"] = dict()

sizes["samd20-xpro"]["deltagen"] = dict()
sizes["samd21-xpro"]["deltagen"] = dict()

### adding samd20-xpro data size ###
processor = "samd20-xpro"
folder_processor = database_diff + processor
folder_samd20 = sorted(os.listdir(folder_processor))
for folder in folder_samd20:
    curr = folder_processor + "/" + folder
    for file in sorted(os.listdir(curr)):
        if not ".log" in file:
            revisions = file.split("_")
            name_file = file
            name_rev2 = revisions[4] + "_" + revisions[5]
            slot_rev2 = name_rev2 + "_" + revisions[6]
            folder_rev2 = database + name_rev2 + "/" + processor + "/" + slot_rev2 + ".bin"
            size_rev2 = os.path.getsize(folder_rev2)
            sizes[processor]["deltagen"][name_file] = dict()
            sizes[processor]["deltagen"][name_file]["size"] = os.path.getsize(curr + "/" + file)
            sizes[processor]["deltagen"][name_file]["check"] = "pass" # no check possible (no patch function)
            sizes[processor]["deltagen"][name_file]["normalized"] = os.path.getsize(curr + "/" + file) / size_rev2

### adding samd21-xpro data size ###
processor = "samd21-xpro"
folder_processor = database_diff + processor
folder_samd21 = sorted(os.listdir(folder_processor))
for folder in folder_samd21:
    curr = folder_processor + "/" + folder
    for file in sorted(os.listdir(curr)):
        if not ".log" in file:
            revisions = file.split("_")
            name_file = file
            name_rev2 = revisions[4] + "_" + revisions[5]
            slot_rev2 = name_rev2 + "_" + revisions[6]
            folder_rev2 = database + name_rev2 + "/" + processor + "/" + slot_rev2 + ".bin"
            size_rev2 = os.path.getsize(folder_rev2)
            sizes[processor]["deltagen"][name_file] = dict()
            sizes[processor]["deltagen"][name_file]["size"] = os.path.getsize(curr + "/" + file)
            sizes[processor]["deltagen"][name_file]["check"] = "pass" # no check possible (no patch function)
            sizes[processor]["deltagen"][name_file]["normalized"] = os.path.getsize(curr + "/" + file) / size_rev2

### saving to JSON-file ###
with open("sizes_sorted_riotboot.save", 'w') as out:
    json.dump(sizes, out)

print("Done!")
