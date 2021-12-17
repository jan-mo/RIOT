#!/usr/bin/env python3

import os, sys

GIT = "../../../"
path = "bin/samd21-xpro/"
file1_in = path
file1_out = path
coaproot = "../../coaproot/fw/samd21-xpro/"

path_files = os.listdir(path)
path_files.sort()
fw_versions_slot0 = list(filter(lambda a: ".riot.bin" in a, path_files))
fw_versions_slot0 = list(filter(lambda a: "slot0" in a, fw_versions_slot0))
fw_versions_slot1 = list(filter(lambda a: ".riot.bin" in a, path_files))
fw_versions_slot1 = list(filter(lambda a: "slot1" in a, fw_versions_slot1))

### check if slot0 or 1 is installed
if "slot0_installed" in path_files:
    ### file1
    file1_in = file1_in + "slot0_installed"
    file1_out = file1_out + "slot0_installed_no_header"
    ### file2
    file2_in = path + fw_versions_slot1[-1]
    os.system("cp " + file2_in + " slot1_new")
    file2_out = path + "slot1_new_no_header"
    ### out file
    out_file = coaproot + fw_versions_slot1[-1]

elif "slot1_installed" in path_files:
    ### file1
    file1_in = file1_in + "slot1_installed"
    file1_out = file1_out + "slot1_installed_no_header"
    ### file2
    file2_in = path + fw_versions_slot0[-1]
    os.system("cp " + file2_in + " slot0_new")
    file2_out = path + "slot0_new_no_header"
    ### out file
    out_file = coaproot + fw_versions_slot0[-1]

### remove header from files
with open(file1_in, 'rb') as f:
    data_file1 = f.read()
with open(file2_in, 'rb') as f:
    data_file2 = f.read()

### remove 256 bytes
with open(file1_out, 'wb') as out:
    out.write(data_file1[256:])
with open(file2_out, 'wb') as out:
    out.write(data_file2[256:])

### store new header
new_header = data_file2[0:256]

os.system(GIT + "minibsdiff/minibsdiff gen " + file1_out + " " + file2_out + " diff_out" + " > silent")
os.system(GIT + "heatshrink/heatshrink -e -w 8 -l 4 diff_out " + out_file + " > silent")
os.system("rm silent")

### add new header to out_file
with open(out_file, 'rb') as f:
    data = f.read()

### remove 256 bytes
with open(out_file, 'wb') as out:
    out.write(new_header)
    out.write(data)

### for debugging
os.system("cp " + out_file + " patch_file")
