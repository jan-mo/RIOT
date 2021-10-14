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
name = sys.argv[1]
name_folder = '../' + name

# check if firmware already exists
revisions = os.listdir("../")
folder_exists = False
if name in revisions:
    print("Revision " + name + " gets overwritten.")
    folder_exists = True
else:
    os.mkdir(name_folder)

for board in boards:
    # create board folder
    if not folder_exists:
        os.mkdir(name_folder + '/' + board)

    # copy bin files
    copyfile(src + board + '/firmware_example.bin', name_folder + '/' + board + '/' + name + '.bin')

    #copy elf files
    copyfile(src + board + '/firmware_example.elf', name_folder + '/' + board + '/' + name + '.elf')

    #copy map files
    copyfile(src + board + '/firmware_example.map', name_folder + '/' + board + '/' + name + '.map')


# save diff of firmware version
os.system("mv " + src + '../firmware.diff ' + name_folder + '/firmware.diff')

if os.path.getsize(name_folder + "/firmware.diff") >= 50000000:
    os.system("split -b50M " + name_folder + "/firmware.diff " + name_folder + "/firmware.diff_split_")
    os.system("rm " + name_folder + "/firmware.diff")

print('Done!')
