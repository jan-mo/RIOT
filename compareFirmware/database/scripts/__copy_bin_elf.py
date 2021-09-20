#!/usr/bin/env python3.9

import os, sys
from shutil import move, copyfile

###
### make sure that firmware is compiled for both boards
### make sure diff file is up to date
###
### for automatic use, run './make_copy.sh'
###

src = '../../../firmwareExample/bin/'

boards = ['samd20-xpro', 'samd21-xpro']

# firmware_name
name = '../' + sys.argv[1]

# check if firmware already exists
try:
    os.mkdir(name)
except FileExistsError:
    print("ERROR: Firmware version exists!")
    sys.exit()

for board in boards:
    # create board folder
    os.mkdir(name + '/' + board)

    # copy bin files
    copyfile(src + board + '/firmware_example.bin', name + '/' + board + '/' + name + '.bin')

    #copy elf files
    copyfile(src + board + '/firmware_example.elf', name + '/' + board + '/' + name + '.elf')

    #copy map files
    copyfile(src + board + '/firmware_example.map', name + '/' + board + '/' + name + '.map')


# save diff of firmware version
move(src + '../firmware.diff', name + '/firmware.diff')

if os.path.getsize(name + "/firmware.diff") >= 50000000:
    os.system("split -b50M " + name + "/firmware.diff " + name + "/firmware.diff_split_")
    os.system("rm " + name + "/firmware.diff")

print('Done!')
