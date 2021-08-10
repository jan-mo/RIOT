#!/usr/bin/env python3.9

from tabulate import tabulate
from _func_compress import compress_function

[results_samd20_zlib, results_samd21_zlib] = compress_function("zlib")
[results_samd20_gzip, results_samd21_gzip] = compress_function("gzip")
[results_samd20_hs, results_samd21_hs] = compress_function("hs")

# print table samd20
entries = []
entry_zlib = []
entry_gzip = []
entry_hs = []
entry_zlib.append("zlib")
entry_gzip.append("gzip")
entry_hs.append("hs")

revisions = sorted(results_samd20_zlib.keys())
for revision in revisions:
    entry_zlib.append(str(results_samd20_zlib[revision]["reduction"]) + "%")
    entry_gzip.append(str(results_samd20_gzip[revision]["reduction"]) + "%")
    entry_hs.append(str(results_samd20_hs[revision]["reduction"]) + "%")

revisions.insert(0,"SAMD20-xpro")
print(tabulate([entry_zlib, entry_gzip, entry_hs], headers = revisions, tablefmt = "tsv"))


print()
print()
# print table samd21
entries = []
entry_zlib = []
entry_gzip = []
entry_hs = []
entry_zlib.append("zlib")
entry_gzip.append("gzip")
entry_hs.append("hs")

revisions = sorted(results_samd21_zlib.keys())
for revision in revisions:
    entry_zlib.append(str(results_samd21_zlib[revision]["reduction"]) + "%")
    entry_gzip.append(str(results_samd21_gzip[revision]["reduction"]) + "%")
    entry_hs.append(str(results_samd21_hs[revision]["reduction"]) + "%")

revisions.insert(0,"SAMD21-xpro")
print(tabulate([entry_zlib, entry_gzip, entry_hs], headers = revisions, tablefmt = "tsv"))
