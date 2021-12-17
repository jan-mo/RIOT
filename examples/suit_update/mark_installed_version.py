#!/usr/bin/env python3

import os, sys

path = "bin/samd21-xpro/"

argument = 0
if len(sys.argv) == 2:
    argument = str(sys.argv[1])

fw_versions = os.listdir(path)
fw_versions.sort()

### remove old firmware installed
os.system("rm -f " + path + "slot0*")
os.system("rm -f " + path + "slot1*")

fw_versions = list(filter(lambda a: ".riot.bin" in a, fw_versions))

if argument == 0:
    ### by flashing only slot0 is flashed
    fw_versions = list(filter(lambda a: "slot0" in a, fw_versions))
    print("installed is ", fw_versions[-1])
    os.system("cp " + path + fw_versions[-1] + " " + path + "slot0_installed")

elif argument == "slot0":
    fw_versions = list(filter(lambda a: "slot0" in a, fw_versions))
    print("installed is ", fw_versions[-1])
    os.system("cp " + path + fw_versions[-1] + " " + path + "slot0_installed")

elif argument == "slot1":
    fw_versions = list(filter(lambda a: "slot1" in a, fw_versions))
    print("installed is ", fw_versions[-1])
    os.system("cp " + path + fw_versions[-1] + " " + path + "slot1_installed")
