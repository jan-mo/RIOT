#!/usr/bin/env python3.9

import heatshrink2 as hs
import os


folder = 'bin_files/'


# compress all bin-files in folder bin_files
files = os.listdir(folder)

# compress
for file in files:
	fin = open(folder + file,'rb').read()

	compress = hs.compress(fin)

	file_name = file[:-4]
	name_compress = file_name + '_heat_compressed'

	fout = open('compressed/' + name_compress, 'wb')
	fout.write(compress)
	fout.close()


# decompress
for file in files:
	
	file_name = file[:-4]
	name_compress = file_name + '_heat_compressed'
	name_decompress = file_name + '_heat_decompressed.bin'

	fout = open('compressed/' + name_compress, 'rb').read()

	decompress = hs.decompress(fout)

	fout = open('decompressed/' + name_decompress, 'wb')
	fout.write(decompress)
	fout.close()
