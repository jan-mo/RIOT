#!/usr/bin/env python3.8

import os

from sys import path
path.append("../../_helper_functions/")
from __finding_versions import SearchDatabase

### define the revs that need to be calculated     ###
###   - calculates the defined rev with all others ###
###   - setting rev = ["all"] for full calculation ###
revs = ['rev_12']

Database = SearchDatabase("../../data_basis")
versions = Database.database_get_revisions()

### calculate DG diff ###
if "all" in revs:
    for rev1 in versions:
        for rev2 in versions:
            os.system(".\deltagen_diff.bat " + rev1 + " " + rev2)
else:
    for rev1 in revs:
        for rev2 in versions:
            os.system(".\deltagen_diff.bat " + rev1 + " " + rev2)
    for rev1 in versions:
        for rev2 in revs:
            os.system(".\deltagen_diff.bat " + rev1 + " " + rev2)
