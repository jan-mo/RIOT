#!/usr/bin/env python3

import os

### calculates and plots the differences of revisions and of the slots

# difference of revisions
os.system("cd difference/scripts && ./difference.py")
os.system("cd difference/scripts && ./plot_differences.py")

# difference of slots
os.system("cd difference/scripts && ./difference_riotboot.py")
os.system("cd difference/scripts && ./plot_differences_slots.py")
