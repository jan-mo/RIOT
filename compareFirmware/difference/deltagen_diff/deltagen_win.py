#!/usr/bin/env python3

import os

from sys import path
path.append("..\..\_helper_functions")
from __finding_versions import SearchDatabase

### define the revs that need to be calculated     ###
###   - calculates the defined rev with all others ###
###   - setting rev = ["all"] for full calculation ###
revs = ['all']

databasis = "data_basis"

Database = SearchDatabase("../../" + databasis)
versions = Database.database_get_revisions()

os.system("mkdir " + databasis)
os.system("mkdir " + databasis + "/samd20-xpro")
os.system("mkdir " + databasis + "/samd21-xpro")

### calculate DG diff ###
if "all" in revs:
    for rev1 in versions:
        for rev2 in versions:
            os.system(".\deltagen_diff.bat " + rev1 + " " + rev2 + " " + databasis)
else:
    for rev1 in revs:
        for rev2 in versions:
            os.system(".\deltagen_diff.bat " + rev1 + " " + rev2 + " " + databasis)
    for rev1 in versions:
        for rev2 in revs:
            os.system(".\deltagen_diff.bat " + rev1 + " " + rev2 + " " + databasis)

# collecting sizes
os.system("python _collect_sizes.py")
