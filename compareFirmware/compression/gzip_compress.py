#!/usr/bin/env python3.9

import gzip
import os

# list all files in database
data = os.listdir('../database')
versions = []
folders_samd20 = []
folders_samd21 = []

# create path for samd20 and samd21
for version in data:
	if os.path.isdir(os.path.join('../database/' + version)):
		versions.append(version)
		folders_samd20.append('../database/' + version + '/samd20-xpro/')
		folders_samd21.append('../database/' + version + '/samd21-xpro/')

# samd20-xpro
for i, folder in enumerate(folders_samd20):
	# compress
	f = open(folder + versions[i] + '.bin', 'rb').read()
	compress = gzip.compress(f)

	name_compress = versions[i] + '_gzip_compressed'

	f = open('compressed/samd20-xpro/' + name_compress, 'wb')
	f.write(compress)
	f.close()

	# decompress
	name_compress = versions[i] + '_gzip_compressed'
	name_decompress = versions[i] + '_gzip_decompressed.bin'

	f = open('compressed/samd20-xpro/' + name_compress, 'rb').read()
	decompress = gzip.decompress(f)

	f = open('decompressed/samd20-xpro/' + name_decompress, 'wb')
	f.write(decompress)
	f.close()

# samd21-xpro
for i, folder in enumerate(folders_samd21):
	# compress
	f = open(folder + versions[i] + '.bin', 'rb').read()
	compress = gzip.compress(f)

	name_compress = versions[i] + '_gzip_compressed'

	f = open('compressed/samd21-xpro/' + name_compress, 'wb')
	f.write(compress)
	f.close()

	# decompress
	name_compress = versions[i] + '_gzip_compressed'
	name_decompress = versions[i] + '_gzip_decompressed.bin'

	f = open('compressed/samd21-xpro/' + name_compress, 'rb').read()
	decompress = gzip.decompress(f)

	f = open('decompressed/samd21-xpro/' + name_decompress, 'wb')
	f.write(decompress)
	f.close()
