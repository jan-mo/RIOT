#!/usr/bin/env python3

import os
from matplotlib import pyplot as plt

from sys import path
path.append("../../_helper_functions/")
from __finding_versions import SearchDatabase
from __plot_functions import plot_bar

###
### plots the sizes of each revision
###

# searching revisions for samd20 and samd21
Database = SearchDatabase("../")
samd20, samd21, versions = Database.database_files()

size_samd20 = []
size_samd21 = []

for i, version in enumerate(versions):
    size_samd20.append(os.path.getsize(samd20[i])/1024)
    size_samd21.append(os.path.getsize(samd21[i])/1024)

fig, ax = plot_bar([size_samd20, size_samd21], versions, ["samd20-xpro", "samd21-xpro"], False, figsize = (10,6), width = 0.4)

fig.savefig("../plots/sizes_revisions.pdf")
plt.close("all")

print("Done!")
