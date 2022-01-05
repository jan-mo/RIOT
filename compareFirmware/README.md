# compareFirmware

This folder holds all scripts and files for the firmware comparison. The folders are:
- \_helper_functions
- external_algorithms
- data_basis
- difference
- compression
- matches_diff

The script `compress_difference.py` saves the database info and executes the compression and difference scripts of the complete data_basis.

The script `difference_and_plot_all.py` calculates all differences and also the difference with the slots. This script further creates the plots for all values.

## requirements

The `requirements.txt` holds all python requirements.
Some compression or differencing algorithms need external GIT repository. Possible algorithms are `minibsdiff`, `heatshrink`, `vcdiff`, `zdelta` or `miniz`. These can be find in folder `external_algorithms`

## \_helper_functions

This folder contains helper functions for plotting and finding revision-data.

## external_algorithms

Here all compiled algorithms are stored. In folder `external_algorihtms/Repos/` all repositories are stored. (use `git submodule update --init --recursive`)

## data_basis

This folder holds all compiled revisions for the samd20-xpro and samd21-xpro board. Also the revision information is saved here.

## difference

In this folder the difference of the complete data basis is calculated. It is separated into the difference of the revision and with enabled slots.

## compression

In this folder the the compression step of the data basis is done. The revisions are compressed and also all patch files can be compressed.

## matches_diff

Here the characteristics of the revisions are calculated. The four characteristics are:
- number of chunks
- number of added bytes
- number of deleted bytes
- size of diff file
