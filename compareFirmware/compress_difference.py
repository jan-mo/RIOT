#!/usr/bin/env python3

import os

### saves database info, calculates compression and the differences

os.system("cd database/scripts/ && ./saving_database_info.sh")
os.system("cd compression && ./compress.py && ./compress.py > compress.txt")
os.system("cd difference/scripts && ./difference.py")
