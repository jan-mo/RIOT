#!/usr/bin/env python3.8

import os

### define the revs that need to be calculated     ###
###   - calculates the defined rev with all others ###
###   - setting rev = ["all"] for full calculation ###
revs = ['rev_11']

# database
folder_database = '../../database/'
database = os.listdir(folder_database)
versions = []

### searching path for samd20 and samd21 ###
for version in database:
    if os.path.isdir(os.path.join(folder_database + version)):
        # exclude suit_updater
        if version == "suit_updater":
            continue;

        # collection all versions
        versions.append(version)

versions = sorted(versions)


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
