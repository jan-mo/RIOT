#!/usr/bin/env python3.9

import os
from shutil import copyfile


src = '../firmware_example/bin/'
dst_bin = '/bin_files/'
dst_elf = '/elf_files/'
dst_map = '/map_files/'

boards = ['samd20-xpro', 'samd21-xpro']


name = input('Enter firmware name: ')


for board in boards:
	# copy bin files
	copyfile(src + board + '/firmware_example.bin', board + dst_bin + name + '.bin')

	#copy elf files
	copyfile(src + board + '/firmware_example.elf', board + dst_elf + name + '.elf')

	#copy map files
	copyfile(src + board + '/firmware_example.map', board + dst_map + name + '.map')


# save diff of firmware version
# TODO!!!
