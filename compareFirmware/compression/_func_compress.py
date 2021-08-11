#!/usr/bin/env python3.9

import zlib, gzip, bz2, lzma
import heatshrink2 as hs
import os

###
### methods are zlib, gzip, hs (heatshrink2)
### option for specific method
###
def __all_compress_functions(file, method, option = None):
    if method == "zlib" and option:
        compress = zlib.compress(file, option)
    elif method == "zlib":
        compress = zlib.compress(file)

    elif method == "gzip" and option:
        compress = gzip.compress(file, option)
    elif method == "gzip":
        compress = gzip.compress(file)

    elif method == "hs" and option:
        compress = hs.compress(file, option)
    elif method == "hs":
        compress = hs.compress(file)

    elif method == "bz2" and option:
        compress = bz2.compress(file, option)
    elif method == "bz2":
        compress = bz2.compress(file)

    elif method == "lzma" and option:
        compress = lzma.compress(file, option)
    elif method == "lzma":
        compress = lzma.compress(file)

    return compress

def __all_decompress_functions(file, method, option = None):
    if method == "zlib" and option:
        decompress = zlib.decompress(file, option)
    elif method == "zlib":
        decompress = zlib.decompress(file)

    elif method == "gzip" and option:
        decompress = gzip.decompress(file, option)
    elif method == "gzip":
        decompress = gzip.decompress(file)

    elif method == "hs" and option:
        decompress = hs.decompress(file, option)
    elif method == "hs":
        decompress = hs.decompress(file)

    elif method == "bz2" and option:
        decompress = bz2.decompress(file, option)
    elif method == "bz2":
        decompress = bz2.decompress(file)

    elif method == "lzma" and option:
        decompress = lzma.decompress(file, option)
    elif method == "lzma":
        decompress = lzma.decompress(file)

    return decompress


def compress_database(method, option = None):
    # list all files in database
    data = os.listdir('../database')
    versions = []
    folders_samd20 = []
    folders_samd21 = []

    results_samd20 = dict()
    results_samd21 = dict()

    # create path for samd20 and samd21
    for version in data:
        if os.path.isdir(os.path.join('../database/' + version)):
            # exclude suit_updater
            if version == "suit_updater":
                continue;

            versions.append(version)
            folders_samd20.append('../database/' + version + '/samd20-xpro/')
            folders_samd21.append('../database/' + version + '/samd21-xpro/')

    # samd20-xpro
    for i, folder in enumerate(folders_samd20):
        # dictionary
        result = dict()

        # files
        file_orig = folder + versions[i] + '.bin' 
        file_comp = 'compressed/samd20-xpro/' + versions[i] + '_' + method + '_compressed'
        file_decomp = 'decompressed/samd20-xpro/' +  versions[i] + '_' + method + '_decompressed.bin'

        # compress
        f = open(file_orig, 'rb').read()
        compress = __all_compress_functions(f, method, option)

        # save compressed
        f = open(file_comp, 'wb')
        f.write(compress)
        f.close()

        # decompress
        f = open(file_comp, 'rb').read()
        decompress = __all_decompress_functions(f, method, option)

        # save decompressed
        f = open(file_decomp, 'wb')
        f.write(decompress)
        f.close()

        # check if compression worked
        result["result"] = "pass" if os.path.getsize(file_orig) == os.path.getsize(file_decomp) else "fail"
        result["size_orig"] = os.path.getsize(file_orig)
        result["size_comp"] = os.path.getsize(file_comp)
        result["size_decomp"] = os.path.getsize(file_decomp)
        result["reduction"] = round(os.path.getsize(file_comp) / os.path.getsize(file_decomp) * 100, 2)
        results_samd20[str(versions[i])] = result

    # samd21-xpro
    for i, folder in enumerate(folders_samd21):
        # dictionary
        result = dict()

        # files
        file_orig = folder + versions[i] + '.bin' 
        file_comp = 'compressed/samd21-xpro/' + versions[i] + '_' + method + '_compressed'
        file_decomp = 'decompressed/samd21-xpro/' +  versions[i] + '_' + method + '_decompressed.bin'

        # compress
        f = open(folder + versions[i] + '.bin', 'rb').read()
        compress = __all_compress_functions(f, method, option)

        f = open(file_comp, 'wb')
        f.write(compress)
        f.close()

        # decompress
        f = open(file_comp, 'rb').read()
        decompress = __all_decompress_functions(f, method, option)

        f = open(file_decomp, 'wb')
        f.write(decompress)
        f.close()

        
        # check if compression worked
        result["result"] = "pass" if os.path.getsize(file_orig) == os.path.getsize(file_decomp) else "fail"
        result["size_orig"] = os.path.getsize(file_orig)
        result["size_comp"] = os.path.getsize(file_comp)
        result["size_decomp"] = os.path.getsize(file_decomp)
        result["reduction"] = round(os.path.getsize(file_comp) / os.path.getsize(file_decomp) * 100, 2)
        results_samd21[str(versions[i])] = result

    return results_samd20, results_samd21
