#!/usr/bin/env python3.9

import zlib, gzip, bz2, lzma
import heatshrink2 as hs
import os

from sys import path
path.append("../../_helper_functions/")
from __finding_versions import SearchDatabase

###
### methods are zlib, gzip, hs (heatshrink2), bz2 and lzma
### option for specific method
###
def __all_compress_functions(file, method, option = None):

    folder_GIT = "../../../../"

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

    elif method == "miniz" and option:
        f = open("temp/temp_in", 'wb')
        f.write(file)
        f.close()
        os.system("./" + folder_GIT + "miniz/miniz_tester " + option + " c temp/temp_in temp/temp_out > temp/silent")
        compress = open("temp/temp_out", 'rb').read()
    elif method == "miniz":
        f = open("temp/temp_in", 'wb')
        f.write(file)
        f.close()
        os.system("./" + folder_GIT + "miniz/miniz_tester c " + file + " temp/temp_in temp/temp_out > temp/silent")
        compress = open("temp/temp_out", 'rb').read()

    else:
        print("Warning: method " + method + " not implemented.")

    return compress

def __all_decompress_functions(file, method, option = None):

    folder_GIT = "../../../../"

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

    elif method == "miniz" and option:
        f = open("temp/temp_in", 'wb')
        f.write(file)
        f.close()
        os.system("./" + folder_GIT + "miniz/miniz_tester " + option + " d temp/temp_in temp/temp_out > temp/silent")
        decompress = open("temp/temp_out", 'rb').read()
    elif method == "miniz":
        f = open("temp/temp_in", 'wb')
        f.write(file)
        f.close()
        os.system("./" + folder_GIT + "miniz/miniz_tester d " + file + " temp/temp_in temp/temp_out > temp/silent")
        decompress = open("temp/temp_out", 'rb').read()

    return decompress

###
### compresses and decompresses the data
###
def _compress_decompress_file(file_orig, name, processor, method, option):

        result = dict()

        file_comp = '../compressed/' + processor + '/' + name + '_' + method + '_compressed'
        file_decomp = '../decompressed/' + processor + '/' +  name + '_' + method + '_decompressed.bin'

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
        result["reduction"] = round(os.path.getsize(file_comp) / os.path.getsize(file_decomp), 4)

        return result

###
### compresses all revisions in database
###
def compress_database(method, option = None):
    # find all folders in database
    Database = SearchDatabase("../../data_basis/")
    [folders_samd20,folders_samd21,versions] = Database.database_get_revision_folders()

    results_samd20 = dict()
    results_samd21 = dict()

    # create temp folder
    os.system("mkdir temp")

    # samd20-xpro
    for i, folder in enumerate(folders_samd20):
        # files
        file_orig = folder + versions[i] + '.bin'

        result = _compress_decompress_file(file_orig, versions[i], "samd20-xpro", method, option)

        results_samd20[str(versions[i])] = result

    # samd21-xpro
    for i, folder in enumerate(folders_samd21):
        # files
        file_orig = folder + versions[i] + '.bin'

        result = _compress_decompress_file(file_orig, versions[i], "samd21-xpro", method, option)

        results_samd21[str(versions[i])] = result

    # remove all temp files
    os.system("rm -r temp")

    return results_samd20, results_samd21

###
### function that compresses all files with given compression method
###
def compress_files(files, methods, option = None):
    results = dict()


    for method in methods:
        results[method] = dict()
        if method == "miniz":
            option = "-m1"
        for file in files:
            split_file = file.split("/")
            name = split_file[-1]
            result = _compress_decompress_file(file, name, "samd20-xpro", method, option)
            results[method][name] = result
    
    return results
