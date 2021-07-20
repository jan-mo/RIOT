#!/usr/bin/env python3.9

import gzip
import os

board_folder = ['../database/samd20-xpro/bin_files/', '../database/samd21-xpro/bin_files/']


for folder in board_folder:
	# compress all bin-files in folder bin_files
	files = os.listdir(folder)

	# compress
	for file in files:
		f = open(folder + file, 'rb').read()
		compress = gzip.compress(f)

		file_name = file[:-4]
		name_compress = file_name + '_gzip_compressed'

		f = open('compressed/' + name_compress, 'wb')
		f.write(compress)
		f.close()


	# decompress
	for file in files:

		file_name = file[:-4]
		name_compress = file_name + '_gzip_compressed'
		name_decompress = file_name + '_gzip_decompressed.bin'

		f = open('compressed/' + name_compress, 'rb').read()
		decompress = gzip.decompress(f)

		f = open('decompressed/' + name_decompress, 'wb')
		f.write(decompress)
		f.close()
