#!/usr/bin/env python3

import os

external_path = "../../external_algorithms/"

### remove all old fw_xx ###
os.system("rm fw_*")

print("Test minibsdiff:")
os.system("valgrind --log-file=output ./" + external_path + "minibsdiff gen suit_update-slot0.bin suit_update-slot1.bin minibsdiff > silent")
os.system("valgrind --log-file=output ./" + external_path + "minibsdiff app suit_update-slot0.bin minibsdiff fw_minibsdiff  > silent")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest heatshrink")
os.system("valgrind --log-file=output ./" + external_path + "heatshrink -e -w8 -l4 minibsdiff comp_heatshrink > silent")
os.system("valgrind --log-file=output ./" + external_path + "heatshrink -d -w8 -l4 comp_heatshrink decomp_heatshrink > silent")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest bsdiff")
os.system("valgrind --log-file=output bsdiff suit_update-slot0.bin suit_update-slot1.bin bsdiff > silent")
os.system("valgrind --log-file=output bspatch suit_update-slot0.bin fw_bsdiff bsdiff > silent")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest zdelta")
os.system("valgrind --log-file=output ./" + external_path + "zdc suit_update-slot0.bin suit_update-slot1.bin zdelta > silent")
os.system("valgrind --log-file=output ./" + external_path + "zdu suit_update-slot0.bin zdelta fw_zdelta > silent")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest vcdiff")
os.system("valgrind --log-file=output ./" + external_path + "vcdiff encode -dictionary suit_update-slot0.bin < suit_update-slot1.bin > vcdiff")
os.system("valgrind --log-file=output ./" + external_path + "vcdiff decode -dictionary suit_update-slot0.bin < vcdiff > fw_vcdiff")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest xdelta3")
os.system("valgrind --log-file=output xdelta3 -e -S -N -D -R -s suit_update-slot0.bin  suit_update-slot1.bin xdelta3")
os.system("valgrind --log-file=output xdelta3 -d -s suit_update-slot0.bin xdelta3 fw_xdelta3")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

print("\n\nTest detools")
os.system("python -m detools create_patch -t sequential -c heatshrink -a match-blocks suit_update-slot0.bin suit_update-slot1.bin detools > silent")
os.system("valgrind --log-file=output ./func_detools apply_patch suit_update-slot0.bin detools fw_detools")
os.system("grep -ri \"heap usage\"")
os.system("rm output")

os.system("rm output silent")
