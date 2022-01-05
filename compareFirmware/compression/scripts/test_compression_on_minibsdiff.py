#!/usr/bin/env python3

import os

external_path = "../../external_algorithms/"

print("Test minibsdiff:")
os.system("valgrind --log-file=output ./../minibsdiff/minibsdiff gen suit_update-slot0.bin suit_update-slot1.bin minibsdiff > silent")
os.system("valgrind --log-file=output ./../minibsdiff/minibsdiff app suit_update-slot0.bin minibsdiff fw_minibsdiff  > silent")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest heatshrink")
os.system("valgrind --log-file=output ./../heatshrink/heatshrink -e -w8 -l4 minibsdiff comp_heatshrink > silent")
os.system("valgrind --log-file=output ./../heatshrink/heatshrink -d -w8 -l4 comp_heatshrink decomp_heatshrink > silent")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest bsdiff")
os.system("valgrind --log-file=output ./../bsdiff/bsdiff suit_update-slot0.bin suit_update-slot1.bin bsdiff > silent")
os.system("valgrind --log-file=output ./../bsdiff/bspatch suit_update-slot0.bin fw_bsdiff bsdiff > silent")
os.system("grep -ri \"heap usage\"")

print("\n\nTest zdelta")
os.system("valgrind --log-file=output ./../zdelta/zdc suit_update-slot0.bin suit_update-slot1.bin zdelta > silent")
os.system("valgrind --log-file=output ./../zdelta/zdu suit_update-slot0.bin zdelta fw_zdelta > silent")
os.system("grep -ri \"heap usage\"")

print("\n\nTest vcdiff")
os.system("valgrind --log-file=output ./../vcdiff/vcdiff encode -dictionary suit_update-slot0.bin < suit_update-slot1.bin > vcdiff")
os.system("valgrind --log-file=output ./../vcdiff/vcdiff decode -dictionary suit_update-slot0.bin < vcdiff > fw_vcdiff")
os.system("grep -ri \"heap usage\"")

print("\n\nTest detools")
os.system("python -m detools create_patch_in_place --memory-size 10240 --segment-size 256 -c heatshrink  suit_update-slot0.bin suit_update-slot1.bin detools > silent")
os.system("cp suit_update-slot0.bin fw_detools")
os.system("valgrind --log-file=output ./func_detools apply_patch_in_place fw_detools detools")
os.system("grep -ri \"heap usage\"")


os.system("rm output silent")
