#!/usr/bin/env python3.9

import os
from __finding_versions import database_files_riotboot

###
### calculates quick differences in firmware-database (only bsdiff and xdelta3)
###

# used differencing algos
diff_algos = ["diff", "bsdiff", "xdelta3", "rsync8", "rsync16", "rsync32", "detools_none", "detools_heat"]

# database
versions = []
files_samd20 = []
files_samd21 = []

[files_samd20, files_samd21, versions] = database_files_riotboot()

for file in files_samd20:
    print(file)

for file in files_samd21:
    print(file)

print(versions)