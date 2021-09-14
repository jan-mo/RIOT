#!/usr/bin/env python3.9

import os
from __finding_versions import database_files

###
### calculates quick differences in firmware-database (only bsdiff and xdelta3)
###

# used differencing algos
diff_algos = ["bsdiff", "xdelta3"]

# database
versions = []
files_samd20 = []
files_samd21 = []

[files_samd20, files_samd21, versions] = database_files()

folder = "algo_diffs/"
folder_restore = "algo_diffs/restore/"

### clear algo_diffs folder ###
os.system("mkdir " + folder_restore)

### SAMD20-xpro ###
name_arch = "samd20-xpro"
print("SAMD20 bsdiff:")
for i, file1 in enumerate(files_samd20[:-1]):
    j = i+1
    file2 = files_samd20[j]
    #### bsdiff ####
    if "bsdiff" in diff_algos:
        name_bsdiff = "bsdiff_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
        patch_bsdiff = folder + "bsdiff/" + name_arch + "/" + name_bsdiff
        restore_bsdiff = folder_restore + name_bsdiff
        # diff file
        os.system("bsdiff " + file1 + " " + file2 + " " + patch_bsdiff)
        # patch file
        os.system("bspatch " + file1 + " " + restore_bsdiff + " " + patch_bsdiff)
        if os.path.getsize(restore_bsdiff) == os.path.getsize(file2):
            print("Size between rev_" + str(i).zfill(2) + " and rev_" + str(i+1).zfill(2) + ": " + str(round(os.path.getsize(patch_bsdiff)/1024, 2)) + "kB")
        else:
            print("Warning: sizes after restore are not the same!")


### SAMD20-xpro ###
name_arch = "samd20-xpro"
print()
print("SAMD20 xdelta3:")
for i, file1 in enumerate(files_samd20[:-1]):
    j = i+1
    file2 = files_samd20[j]
    #### xdelta3 ####
    if "xdelta3" in diff_algos:
        name_xdelta3 = "xdelta3_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
        patch_xdelta3 = folder + "xdelta3/" + name_arch + "/" + name_xdelta3
        restore_xdelta3 = folder_restore + name_xdelta3
        # diff file
        os.system("xdelta3 -f -e -S -N -D -R -s " + file1 + " " + file2 + " " + patch_xdelta3)
        # patch file
        os.system("xdelta3 -d -s " + file1 + " " + patch_xdelta3 + " " + restore_xdelta3)
        if os.path.getsize(restore_xdelta3) == os.path.getsize(file2):
            print("Size between rev_" + str(i).zfill(2) + " and rev_" + str(i+1).zfill(2) + ": " + str(round(os.path.getsize(patch_xdelta3)/1024, 2)) + "kB")
        else:
            print("Warning: sizes after restore are not the same!")


### clear data ###
os.system("rm -r " + folder_restore)
