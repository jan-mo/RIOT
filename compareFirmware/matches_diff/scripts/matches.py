#!/usr/bin/env python3.9

import os, subprocess, json

###
### calculates the distinction between the revision and with enabled slots
### calculates just between the revision, with alternating slots and with every second revision (update in same slot)
### results are stored in 'diffs_matches.save'
###

from sys import path
path.append("../../difference/scripts/")
from __finding_versions import database_files, database_files_riotboot

# load database with revisions and slots
[files_samd20, files_samd21, versions] = database_files()
[files_samd20_riotboot, files_samd21_riotboot, versions] = database_files_riotboot()

### convert bin-files for line based diff ###
files_all = files_samd20 + files_samd20_riotboot + files_samd21 + files_samd21_riotboot
new_path = "../converted_bins/"

# clear older files
os.system("rm -r " + new_path)
os.system("mkdir " + new_path)
os.system("mkdir " + new_path + "samd20-xpro")
os.system("mkdir " + new_path + "samd21-xpro")

# save converted files
conv_files = []

for file in files_all:
    with open(file, 'rb') as f:
        data_hex = f.read().hex()
    new_data = ""
    for idx in range(0,len(data_hex),2):
        new_data = new_data + data_hex[idx:idx+2] + "\n"

    split_file = file.split("/")
    file_name = new_path + split_file[-2] + "/" + split_file[-1] + "_conv"
    conv_files.append(file_name)

    out = open(file_name, 'w+')
    out.write(new_data)


### diff between all converted data ###
diff_path = "../diff_converted_bins/"

# clear older files
os.system("rm -r " + diff_path)
os.system("mkdir " + diff_path)
os.system("mkdir " + diff_path + "samd20-xpro")
os.system("mkdir " + diff_path + "samd21-xpro")

# save differences
diffs_all = dict()
diffs_all["samd20-xpro"] = dict()
diffs_all["samd21-xpro"] = dict()
diffs_all["samd20-xpro"]["revisions"] = dict()
diffs_all["samd20-xpro"]["slots"] = dict()
diffs_all["samd20-xpro"]["slots"]["second"] = dict()
diffs_all["samd20-xpro"]["slots"]["alternating"] = dict()
diffs_all["samd21-xpro"]["revisions"] = dict()
diffs_all["samd21-xpro"]["slots"] = dict()
diffs_all["samd21-xpro"]["slots"]["second"] = dict()
diffs_all["samd21-xpro"]["slots"]["alternating"] = dict()

# lengths
len_revs_samd20 = len(files_samd20)
len_slots_samd20 = len(files_samd20_riotboot)
len_revs_samd21 = len(files_samd21)
len_slots_samd21 = len(files_samd21_riotboot)



def __get_revision_num(file):
    tmp = file.split("/")
    tmp = tmp[-1].split(".")
    tmp = tmp[-2]

    return tmp[4:]

def __calc_matches(idx1, idx2, path, files):
    diff_name = "diff_" + __get_revision_num(conv_files[idx1]) + "_" + __get_revision_num(conv_files[idx2])
    os.system("diff -a " + conv_files[idx1] + " " + conv_files[idx2] + " > " + path + diff_name)
    nchunks = int(subprocess.check_output("grep \"^---\" " + path + diff_name + " | wc -l", shell=True))
    nbytes_removed = int(subprocess.check_output("grep \"^<\" " + path + diff_name + " | wc -l", shell=True))
    nbytes_added = int(subprocess.check_output("grep \"^>\" " + path + diff_name + " | wc -l", shell=True))
    #nbytes = nbytes_added - nbytes_removed

    return diff_name, nchunks, nbytes_removed, nbytes_added



### diff loop over all ###
for idx in range(len(versions)-1):
    # samd20-xpro
    path = diff_path + "samd20-xpro/"
    offset = 0
    
    # diagonal diff
    idx1 = idx
    idx2 = idx + 1
    diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
    # save to dict
    diffs_all["samd20-xpro"]["revisions"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}

    offset = len_revs_samd20
    # slots every second rev
    # even slots in slot0
    if (idx % 2) == 0:
        idx1 = offset + idx * 2
        idx2 = offset + idx * 2 + 4
        if idx2 < (offset + len_slots_samd20):
            diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
            # save to dict
            diffs_all["samd20-xpro"]["slots"]["second"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}
    # odd slots in slot1
    else:
        idx1 = offset + (idx - 1) * 2 + 3
        idx2 = offset + (idx - 1) * 2 + 3 + 4
        if idx2 < (offset + len_slots_samd20):
            diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
            # save to dict
            diffs_all["samd20-xpro"]["slots"]["second"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}
    # slots alternating
    # even count
    if (idx % 2) == 0:
        idx1 = offset + idx * 2
        idx2 = offset + idx * 2 + 3
        diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
        # save to dict
        diffs_all["samd20-xpro"]["slots"]["alternating"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}
    # odd count
    else:
        idx1 = offset + idx * 2 + 1
        idx2 = offset + idx * 2 - 1 + 3
        diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
        # save to dict
        diffs_all["samd20-xpro"]["slots"]["alternating"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}


    # samd21-xpro
    path = diff_path + "samd21-xpro/"
    offset = len_revs_samd20 + len_slots_samd20

    # diagonal diff
    idx1 = idx + offset
    idx2 = idx + offset + 1
    diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
    # save to dict
    diffs_all["samd21-xpro"]["revisions"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}

    offset = len_revs_samd20 + len_slots_samd20 + len_revs_samd21
    # slots every second rev
    # even slots in slot0
    if (idx % 2) == 0:
        idx1 = offset + idx * 2
        idx2 = offset + idx * 2 + 4
        if idx2 < (offset + len_slots_samd21):
            diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
            # save to dict
            diffs_all["samd21-xpro"]["slots"]["second"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}
    # odd slots in slot1
    else:
        idx1 = offset + (idx - 1) * 2 + 3
        idx2 = offset + (idx - 1) * 2 + 3 + 4
        if idx2 < (offset + len_slots_samd21):
            diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
            # save to dict
            diffs_all["samd21-xpro"]["slots"]["second"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}
    # slots alternating
    # even count
    if (idx % 2) == 0:
        idx1 = offset + idx * 2
        idx2 = offset + idx * 2 + 3
        diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
        # save to dict
        diffs_all["samd21-xpro"]["slots"]["alternating"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}
    # odd count
    else:
        idx1 = offset + idx * 2 + 1
        idx2 = offset + idx * 2 - 1 + 3
        diff_name, nchunks, nbytes_removed, nbytes_added = __calc_matches(idx1, idx2, path, conv_files)
        # save to dict
        diffs_all["samd21-xpro"]["slots"]["alternating"][diff_name] = {"chunks":nchunks, "deleted":nbytes_removed, "added":nbytes_added}


### saving diffs ###
with open("../output/diffs_matches.save", 'w') as out:
    json.dump(diffs_all, out)
