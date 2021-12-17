#!/usr/bin/env python3

import os, sys

args = sys.argv
file1 = args[1]
file2 = args[2]
out = args[3]
path = args[4]

### save file2
os.system("cp " + file2 + " temp")

os.system(path + "minibsdiff/minibsdiff gen " + file1 + " " + file2 + " diff_out" + " > silent")
os.system("rm silent")

### for testing, use diff_out as size
os.system("cp diff_out " + out)
