#!/usr/bin/env python3.9

import os

###
### calculates quick differences in firmware-database (only bsdiff and xdelta3)
###

# used differencing algos
diff_algos = ["bsdiff", "xdelta3"]

# database
database = os.listdir('../database')
versions = []
files_samd20 = []
files_samd21 = []

### searching path for samd20 and samd21 ###
for version in database:
    if os.path.isdir(os.path.join('../database/' + version)):
        # exclude suit_updater
        if version == "suit_updater":
            continue;

        # collection all versions
        versions.append(version)
        files_samd20.append('../database/' + version + '/samd20-xpro/' + version + '.bin')
        files_samd21.append('../database/' + version + '/samd21-xpro/' + version + '.bin')

        # remove old files
        os.system("rm -rf ../database/" + version + '/samd20-xpro/' + version + '.bin_*')
        os.system("rm -rf ../database/" + version + '/samd21-xpro/' + version + '.bin_*')

files_samd20 = sorted(files_samd20)
files_samd21 = sorted(files_samd21)
versions = sorted(versions)

folder = "algo_diffs/"
folder_restore = "algo_diffs/restore/"

### clear algo_diffs folder ###
os.system("sudo rm -r " + folder)
os.system("mkdir " + folder)
os.system("mkdir " + folder_restore)

### create algo folders ###
for algo in diff_algos:
    os.system("mkdir " + folder + algo)
    os.system("mkdir " + folder + algo + "/samd20-xpro/")
    os.system("mkdir " + folder + algo + "/samd21-xpro/")

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
        os.system("xdelta3 -e -S -N -D -R -s " + file1 + " " + file2 + " " + patch_xdelta3)
        # patch file
        os.system("xdelta3 -d -s " + file1 + " " + patch_xdelta3 + " " + restore_xdelta3)
        if os.path.getsize(restore_xdelta3) == os.path.getsize(file2):
            print("Size between rev_" + str(i).zfill(2) + " and rev_" + str(i+1).zfill(2) + ": " + str(round(os.path.getsize(patch_xdelta3)/1024, 2)) + "kB")
        else:
            print("Warning: sizes after restore are not the same!")


### clear data ###
os.system("rm -r " + folder_restore)
