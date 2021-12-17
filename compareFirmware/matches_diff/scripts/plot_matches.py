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
plot_function_matches(matches_samd20["revisions"], matches_samd21["revisions"], "compare characteristics of series revisions", "revisions.pdf", "../plots/")

### plot slots alternating ###
plot_function_matches(matches_samd20["slots"]["alternating"], matches_samd21["slots"]["alternating"], "compare characteristics of revisions in alternating slots", "alternating.pdf", "../plots/")

### plot slots second rev ###
plot_function_matches(matches_samd20["slots"]["second"], matches_samd21["slots"]["second"], "compare characteristics of every second revision in same slot", "second.pdf", "../plots/")

### plot same_revision rev ###
plot_function_matches(matches_samd20["slots"]["same_revision"], matches_samd21["slots"]["same_revision"], "compare characteristics between the two different slots", "same_revision.pdf", "../plots/")

print("Done!")
