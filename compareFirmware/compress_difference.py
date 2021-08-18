#!/usr/bin/env python3.9

import os

os.system("cd compression && ./compress.py && ./compress.py > compress.txt && git tag -n *rev* > code_diff.txt")
os.system("cd difference && ./difference.py")
