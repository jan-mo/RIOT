#!/usr/bin/env python3.9

# make sure that firmware is compiled for both boards
# make sure diff file is up to date
#
# for automatic use, run './make_copy.sh'


import os, sys
from shutil import copyfile


src = '../firmware_example/bin/'

boards = ['samd20-xpro', 'samd21-xpro']

# enter firmware_name
name = input('Enter firmware name: ')

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
copyfile(src + '../firmware.diff', name + '/firmware.diff')

print('Done!')
