#!/usr/bin/env python3.9

from tabulate import tabulate
from _func_compress import compress_database

# compress functions
compress_func = ["zlib","gzip","hs","bz2","lzma"]

entries_samd20 = []
entries_samd21 = []

# compress database
for comp in compress_func:
    [SAMD20, SAMD21] = compress_database(comp)

    # calc SAMD20 and SAMD21 entries
    entry_samd20 = []
    entry_samd21 = []
    entry_samd20.append(comp)
    entry_samd21.append(comp)

    revisions_samd20 = sorted(SAMD20.keys())
    for revision in revisions_samd20:
        entry_samd20.append(str(SAMD20[revision]["reduction"]) + "%")
        if (SAMD20[revision]["result"] != "pass"):
            print("SAMD20: " + revision + " with " + comp + " failed!")

    revisions_samd21 = sorted(SAMD21.keys())
    for revision in revisions_samd21:
        entry_samd21.append(str(SAMD21[revision]["reduction"]) + "%")
        if (SAMD21[revision]["result"] != "pass"):
            print("SAMD21: " + revision + " with " + comp + " failed!")

    entries_samd20.append(entry_samd20)
    entries_samd21.append(entry_samd21)

# print SAMD20 table
revisions_samd20.insert(0,"SAMD20-xpro")
print(tabulate(entries_samd20, headers = revisions_samd20, tablefmt = "tsv"))

print()
# print SAMD21 table
revisions_samd21.insert(0,"SAMD21-xpro")
print(tabulate(entries_samd21, headers = revisions_samd21, tablefmt = "tsv"))
