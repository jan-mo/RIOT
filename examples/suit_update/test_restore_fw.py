#!/usr/bin/env python3

import os, sys

GIT = "../../../"
path = "bin/samd21-xpro/"
patch_file = "patch_file"
patch = "patch_file_no_header"
new_file = "slot1_new"
old_file = path + "slot0_installed_no_header"
restored = "restored_fw"

### read header from files
with open(patch_file, 'rb') as f:
    data = f.read()
with open(patch, 'wb') as out:
    out.write(data[256:])

### store new header
new_header = data[0:256]

os.system(GIT + "heatshrink/heatshrink -d -w 8 -l 4 " + patch + " decode")
os.system(GIT + "minibsdiff/minibsdiff app " + old_file + " decode " + restored)

### add new header to restored
with open(restored, 'rb') as f:
    data = f.read()
with open(restored, 'wb') as out:
	out.write(new_header)
	out.write(data)

### check if files are the same
os.system("diff -a " + new_file + " " + restored)
