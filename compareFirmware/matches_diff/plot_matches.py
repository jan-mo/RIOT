#!/usr/bin/env python3.9

import os, json

from sys import path
path.append("../difference/")
from __plot_functions import plot_function_matches


### load data ###
with open("diffs_matches.save", 'r') as json_file:
    matches = json.load(json_file)

matches_samd20 = matches["samd20-xpro"]
matches_samd21 = matches["samd21-xpro"]

### plot revisions ###
plot_function_matches(matches_samd20["revisions"], matches_samd21["revisions"], "Compare different revisions in", "revisions.pdf", "plots/")

### plot slots alternating ###
plot_function_matches(matches_samd20["slots"]["alternating"], matches_samd21["slots"]["alternating"], "Compare different alternating revisions in", "alternationg.pdf", "plots/")

### plot slots second rev ###
plot_function_matches(matches_samd20["slots"]["second"], matches_samd21["slots"]["second"], "Compare every second revisions in", "second.pdf", "plots/")
