#!/usr/bin/env python3.9

import os, sys

args = sys.argv
file1 = args[1]
file2 = args[2]
out = args[3]
path = args[4]

os.system(path + "minibsdiff/minibsdiff gen " + file1 + " " + file2 + " diff_out" + " > silent")
os.system(path + "miniz/miniz_tester c diff_out " + out + " > silent")
os.system("rm silent diff_out")
