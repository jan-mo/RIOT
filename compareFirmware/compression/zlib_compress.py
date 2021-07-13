#!/usr/bin/env python3.9

import zlib
import os

folder = 'bin_files/'


# compress all bin-files in folder bin_files
files = os.listdir(folder)

# compress
for file in files:
	f = open(folder + file, 'rb').read()
	compress = zlib.compress(f, zlib.Z_BEST_COMPRESSION)

	file_name = file[:-4]
	name_compress = file_name + '_zlib_compressed'

	f = open('compressed/' + name_compress, 'wb')
	f.write(compress)
	f.close()


# decompress
for file in files:

	file_name = file[:-4]
	name_compress = file_name + '_zlib_compressed'
	name_decompress = file_name + '_zlib_decompressed.bin'

	f = open('compressed/' + name_compress, 'rb').read()
	decompress = zlib.decompress(f)

	f = open('decompressed/' + name_decompress, 'wb')
	f.write(decompress)
	f.close()
