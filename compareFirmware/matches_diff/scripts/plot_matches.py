#!/usr/bin/env python3

import os, json

from sys import path
path.append("../../_helper_functions/")
from __plot_functions import plot_function_matches

###
### plots the distinctions in revision, alternating and every second update
###

### load data ###
with open("../output/diffs_matches.save", 'r') as json_file:
    matches = json.load(json_file)

matches_samd20 = matches["samd20-xpro"]
matches_samd21 = matches["samd21-xpro"]

### plot revisions ###
plot_function_matches(matches_samd20["revisions"], matches_samd21["revisions"], False, "revisions.pdf", "../plots/")

### plot slots alternating ###
plot_function_matches(matches_samd20["slots"]["alternating"], matches_samd21["slots"]["alternating"], False, "alternating.pdf", "../plots/")

### plot slots second rev ###
plot_function_matches(matches_samd20["slots"]["second"], matches_samd21["slots"]["second"], False, "second.pdf", "../plots/")

### plot same_revision rev ###
plot_function_matches(matches_samd20["slots"]["same_revision"], matches_samd21["slots"]["same_revision"], False, "same_revision.pdf", "../plots/")

print("Done!")
