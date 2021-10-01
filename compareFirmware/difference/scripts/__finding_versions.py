#!/usr/bin/env python3.9

import os

###
### finds all revision in database
### database_files finds all revision except riotboot folder
### database_files_riotboot finds the revision for riotboot
###

def database_files():
    versions = []
    files_samd20 = []
    files_samd21 = []

    path_database = "../../data_basis/"
    database = os.listdir(path_database)
    
    ### searching path for samd20 and samd21 ###
    for version in database:
        if os.path.isdir(os.path.join(path_database + version)):
            # exclude riotboot
            if version == 'riotboot' or version == 'output' or version == 'scripts':
                continue;

            # collection all versions
            versions.append(version)
            files_samd20.append(path_database + version + '/samd20-xpro/' + version + '.bin')
            files_samd21.append(path_database + version + '/samd21-xpro/' + version + '.bin')

            # remove old files
            os.system("rm -rf " + path_database + version + '/samd20-xpro/' + version + '.bin_*')
            os.system("rm -rf " + path_database  + version + '/samd21-xpro/' + version + '.bin_*')

    files_samd20 = sorted(files_samd20)
    files_samd21 = sorted(files_samd21)
    versions = sorted(versions)

    return [files_samd20, files_samd21, versions]

def database_files_riotboot():
    versions = []
    files_samd20 = []
    files_samd21 = []

    path_database = "../../data_basis/riotboot/"
    database = os.listdir(path_database)
    
    ### searching path for samd20 and samd21 ###
    for version in database:
        if os.path.isdir(os.path.join(path_database + version)):
            # exclude test folder
            if version == 'test':
                continue;

            # collection all versions
            versions.append(version)
            files_samd20.append(path_database + version + '/samd20-xpro/' + version + '_slot0.bin')
            files_samd20.append(path_database + version + '/samd20-xpro/' + version + '_slot1.bin')
            files_samd21.append(path_database + version + '/samd21-xpro/' + version + '_slot0.bin')
            files_samd21.append(path_database + version + '/samd21-xpro/' + version + '_slot1.bin')

            # remove old files
            os.system("rm -rf " + path_database + version + '/samd20-xpro/' + version + '_slot0.bin_*')
            os.system("rm -rf " + path_database  + version + '/samd21-xpro/' + version + '_slot1.bin_*')

    files_samd20 = sorted(files_samd20)
    files_samd21 = sorted(files_samd21)
    versions = sorted(versions)

    return [files_samd20, files_samd21, versions]
