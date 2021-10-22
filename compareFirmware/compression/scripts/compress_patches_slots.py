#!/usr/bin/env python3.9

import json, os
from tabulate import tabulate
from _func_compress import compress_files

from sys import path
path.append("../../_helper_functions/")
from __finding_versions import SearchDatabase


def diagonal_sizes(path_dict, diff_algos, max_rev_number):
    # sizes for compression
    sizes_normal_diagonal = dict()
    sizes_riotboot_diagonal = dict()

    # create temp folder
    os.system("mkdir temp")

    for diff_algo in diff_algos:
        # find diagonal normal
        files = path_dict["normal"][diff_algo]
        diagonal = []
        for i in range(max_rev_number):
            diagonal.append(files[i*(max_rev_number+1)+i+1])
        sizes_normal_diagonal[diff_algo] = compress_files(diagonal, compression_methods)

        # find diagonal riotboot
        files = path_dict["riotboot"][diff_algo]
        diagonal = []
        for i in range(max_rev_number):
            # special case for deltagen
            if diff_algo == "deltagen":
                slot_offset = 4
                rev_offset = max_rev_number+1
                # even revisions
                if (i % 2) == 0:
                    diagonal.append(files[i*slot_offset*rev_offset + slot_offset*(i+1) + 1])
                # odd revisions
                else:        
                    diagonal.append(files[i*slot_offset*rev_offset + slot_offset*(i+1) + 2])
            else:
                diagonal.append(files[i*2])

        sizes_riotboot_diagonal[diff_algo] = compress_files(diagonal, compression_methods)

    # remove all temp files
    os.system("rm -r temp")

    return [sizes_normal_diagonal, sizes_riotboot_diagonal]


Database = SearchDatabase("../../difference/")
[path_samd20,path_samd21] = Database.database_path_all_patches()

compression_methods = ["zlib", "gzip", "bz2", "lzma", "hs", "miniz"]

### samd20 calculating compression diagonal
path_dict = path_samd20
diff_algos = list(path_dict["normal"].keys())
# calc max revision number
last_file = path_dict["normal"][diff_algos[0]][-1]
split_file = last_file.split("_")
max_rev_number = int(split_file[-1])
# sizes for compression
sizes_diagonal_samd20 = dict()
sizes_diagonal_samd20["normal"] = dict()
sizes_diagonal_samd20["riotboot"] = dict()
sizes_diagonal_samd20["normal"], sizes_diagonal_samd20["riotboot"] = diagonal_sizes(path_dict, diff_algos, max_rev_number)

### samd21 calculating compression diagonal
path_dict = path_samd21
diff_algos = list(path_dict["normal"].keys())
# calc max revision number
last_file = path_dict["normal"][diff_algos[0]][-1]
split_file = last_file.split("_")
max_rev_number = int(split_file[-1])
# sizes for compression
sizes_diagonal_samd21 = dict()
sizes_diagonal_samd21["normal"] = dict()
sizes_diagonal_samd21["riotboot"] = dict()
sizes_diagonal_samd21["normal"], sizes_diagonal_samd21["riotboot"] = diagonal_sizes(path_dict, diff_algos, max_rev_number)

### save compression values
with open("../output/compression_diagonal_samd20.save", 'w') as out:
    json.dump(sizes_diagonal_samd20, out)

with open("../output/compression_diagonal_samd21.save", 'w') as out:
    json.dump(sizes_diagonal_samd21, out)
