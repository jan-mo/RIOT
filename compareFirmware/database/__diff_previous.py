#!/usr/bin/env python3.9

import os, sys

# firmware_name
name = sys.argv[1]

# skip rev_00
if name != "rev_00":
	rev2 = name
	rev1 = name[:-2] + str(int(name[-2:]) - 1).zfill(2)

	os.system("git diff " + rev1 + " " + rev2 + " > previous.diff")