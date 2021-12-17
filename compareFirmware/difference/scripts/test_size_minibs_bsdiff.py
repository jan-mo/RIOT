#!/usr/bin/env python3

import json

with open("../output/sizes_sorted.save", 'r') as json_file:
    sizes_sorted = json.load(json_file)
with open("../output/versions.save", 'r') as file:
    versions = json.load(file)

minibs_keys = []
bsdiff_keys = []

for i, elem in enumerate(versions[:-1]):
    rev1 = elem
    rev2 = versions[i+1]
    minibs_keys.append("minibs_heat_" + rev1 + "_" + rev2)
    bsdiff_keys.append("bsdiff_" + rev1 + "_" + rev2)

minibs_sizes = []
bsdiff_sizes = []

for elem in minibs_keys:
    minibs_sizes.append(sizes_sorted["samd21-xpro"]["minibs_heat"][elem]["size"])

for elem in bsdiff_keys:
    bsdiff_sizes.append(sizes_sorted["samd21-xpro"]["bsdiff"][elem]["size"])

print(minibs_sizes)
print(bsdiff_sizes)

for i, elem in enumerate(minibs_sizes):
    print(elem - bsdiff_sizes[i])
