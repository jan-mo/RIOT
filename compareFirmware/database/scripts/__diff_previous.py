#!/usr/bin/env python3.9

import os

###
### calculates the difference between current and previous revision
###

# database
database = os.listdir("../")
versions = []

print("Calculating size.")

# searching path for samd20 and samd21 ###
for version in database:
    if os.path.isdir(version):
        # exclude riotboot, scripts and output folder
        if version == 'riotboot' or version == 'scripts' or version == 'output':
            continue;

        # collection all versions
        versions.append(version)

versions = sorted(versions)
print(versions)

for rev2 in versions:
    if "rev_00" == rev2:
        continue
    rev1 = rev2[:-2] + str(int(rev2[-2:])-1).zfill(2)
    os.system("git diff thesis/" + rev1 + " thesis/" + rev2 + " > previous.diff")
    size = os.path.getsize("previous.diff")
    print("Size " + rev1 + " " + rev2 + ": " + str(round(size/1024, 2)) + "kB")
    # check if file is bigger than 50MB (max_value git)
    if size >= 50000000:
        os.system("split -b50M " + "previous.diff " + "previous.diff_split_")
        os.system("rm previous.diff")
        os.system("mv previous.diff_split_* " + rev2)
    else:
        os.system("mv previous.diff " + rev2)
