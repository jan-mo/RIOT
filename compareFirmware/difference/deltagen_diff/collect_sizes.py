#!/usr/bin/env python3.8

import os, json

folder_samd20 = sorted(os.listdir("samd20-xpro/"))
folder_samd21 = sorted(os.listdir("samd21-xpro/"))

database = "../../database/"


sizes = dict()
sizes["samd20-xpro"] = dict()
sizes["samd21-xpro"] = dict()

sizes["samd20-xpro"]["deltagen"] = dict()
sizes["samd21-xpro"]["deltagen"] = dict()

### adding samd20-xpro data size ###
processor = "samd20-xpro"
for folder in folder_samd20:
    curr = processor + "/" + folder
    for file in sorted(os.listdir(curr)):
        if not ".log" in file:
            name = file.split(".")
            name_file = name[0]
            rev2 = str(name[0][-2:])
            name_rev2 = "rev_" + rev2
            folder_rev2 = database + name_rev2 + "/" + processor + "/" + name_rev2 + ".bin"
            size_rev2 = os.path.getsize(folder_rev2)
            sizes[processor]["deltagen"][name_file] = dict()
            sizes[processor]["deltagen"][name_file]["size"] = os.path.getsize(curr + "/" + file)
            sizes[processor]["deltagen"][name_file]["check"] = "pass" # no check possible (no patch function)
            sizes[processor]["deltagen"][name_file]["normalized"] = os.path.getsize(curr + "/" + file) / size_rev2

### adding samd21-xpro data size ###
processor = "samd21-xpro"
for folder in folder_samd21:
    curr = processor + "/" + folder
    for file in sorted(os.listdir(curr)):
        if not ".log" in file:
            name = file.split(".")
            name_file = name[0]
            rev2 = str(name[0][-2:])
            name_rev2 = "rev_" + rev2
            folder_rev2 = database + name_rev2 + "/" + processor + "/" + name_rev2 + ".bin"
            size_rev2 = os.path.getsize(folder_rev2)
            sizes[processor]["deltagen"][name_file] = dict()
            sizes[processor]["deltagen"][name_file]["size"] = os.path.getsize(curr + "/" + file)
            sizes[processor]["deltagen"][name_file]["check"] = "pass" # no check possible (no patch function)
            sizes[processor]["deltagen"][name_file]["normalized"] = os.path.getsize(curr + "/" + file) / size_rev2

### saving to JSON-file ###
with open("sizes_sorted.save", 'w') as out:
    json.dump(sizes, out)

### saving versions ###
with open("versions.save", 'w') as out:
    json.dump(["deltagen"], out)
