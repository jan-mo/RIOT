#!/usr/bin/env python3

import json, statistics
from tabulate import tabulate
from _func_compress import compress_database

###
### This script compresses all revisions with given compression method
### make sure all revisions are stored in the database
###

# compress functions
compress_func = ["zlib","gzip","bz2","lzma","hs","miniz"]

entries_samd20 = []
entries_samd21 = []

# create dictionary
sizes_compression = dict()
sizes_compression["samd20"] = dict()
sizes_compression["samd21"] = dict()

# compress database
for comp in compress_func:
    sizes_compression["samd20"][comp] = dict()
    sizes_compression["samd21"][comp] = dict()
    if comp == "miniz":
        [SAMD20, SAMD21] = compress_database(comp, "-m1")
        sizes_compression["samd20"][comp] = SAMD20
        sizes_compression["samd21"][comp] = SAMD21
    else:
        [SAMD20, SAMD21] = compress_database(comp)
        sizes_compression["samd20"][comp] = SAMD20
        sizes_compression["samd21"][comp] = SAMD21

    # calc SAMD20 and SAMD21 entries
    entry_samd20 = []
    entry_samd21 = []
    entry_samd20.append(comp)
    entry_samd21.append(comp)

    revisions_samd20 = sorted(SAMD20.keys())
    for revision in revisions_samd20:
        entry_samd20.append(SAMD20[revision]["reduction"]*100)
        if (SAMD20[revision]["result"] != "pass"):
            print("SAMD20: " + revision + " with " + comp + " failed!")

    revisions_samd21 = sorted(SAMD21.keys())
    for revision in revisions_samd21:
        entry_samd21.append(SAMD21[revision]["reduction"]*100)
        if (SAMD21[revision]["result"] != "pass"):
            print("SAMD21: " + revision + " with " + comp + " failed!")

    entries_samd20.append(entry_samd20)
    entries_samd21.append(entry_samd21)

# calc mean and std
revisions_samd20.append("mean/std")
revisions_samd21.append("mean/std")
for i in range(len(entries_samd20)):
    mean = round(statistics.mean(entries_samd20[i][1:]*100), 1)
    std = round(statistics.stdev(entries_samd20[i][1:]*100), 1)
    entries_samd20[i].append(str(mean) + "/" + str(std))

    mean = round(statistics.mean(entries_samd21[i][1:]), 1)
    std = round(statistics.stdev(entries_samd21[i][1:]), 1)
    entries_samd21[i].append(str(mean) + "/" + str(std))

# print SAMD20 table
revisions_samd20.insert(0,"SAMD20-xpro")
print(tabulate(entries_samd20, headers = revisions_samd20, tablefmt = "tsv"))

print()
# print SAMD21 table
revisions_samd21.insert(0,"SAMD21-xpro")
print(tabulate(entries_samd21, headers = revisions_samd21, tablefmt = "tsv"))

### save compression values
with open("../output/sizes_compression_rev.save", 'w') as out:
    json.dump(sizes_compression, out)
