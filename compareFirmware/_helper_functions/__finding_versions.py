#!/usr/bin/env python3.9

import os

###
### finds all revision in database
### database_get_revisions finds all revisions in the data_basis
### database_get_revision_folders finds all folders of revisions
### database_files finds all revision except riotboot folder
### database_files_riotboot finds the revision for riotboot
###

class SearchDatabase:

    def __init__(self, database):
        # check last char of database path
        if database[-1] != "/":
            database = database + "/"
        self.path_database = database
        self.exclude_folders = ["riotboot", "output", "scripts", "plots"]

    def database_get_revisions(self):
        # database
        database = os.listdir(self.path_database)
        revisions = []

        ### searching path for samd20 and samd21 ###
        for revision in database:
            if os.path.isdir(os.path.join(self.path_database, revision)):
                # exclude folders
                if revision in self.exclude_folders:
                    continue;

                # collection all versions
                revisions.append(revision)

        return sorted(revisions)

    def database_get_revision_folders(self):
        data = os.listdir(self.path_database)
        versions = []
        folders_samd20 = []
        folders_samd21 = []

        # create path for samd20 and samd21
        for version in data:
            if os.path.isdir(os.path.join(self.path_database, version)):
                # exclude folders
                if version in self.exclude_folders:
                    continue;

                versions.append(version)
                folders_samd20.append(self.path_database + version + '/samd20-xpro/')
                folders_samd21.append(self.path_database + version + '/samd21-xpro/')
        
        folders_samd20 = sorted(folders_samd20)
        folders_samd21 = sorted(folders_samd21)
        versions = sorted(versions)

        return [folders_samd20, folders_samd21, versions]

    def database_files(self):
        versions = []
        files_samd20 = []
        files_samd21 = []

        database = os.listdir(self.path_database)
        
        ### searching path for samd20 and samd21 ###
        for version in database:
            if os.path.isdir(os.path.join(self.path_database, version)):
                # exclude folders
                if version in self.exclude_folders:
                    continue;

                # collection all versions
                versions.append(version)
                files_samd20.append(self.path_database + version + '/samd20-xpro/' + version + '.bin')
                files_samd21.append(self.path_database + version + '/samd21-xpro/' + version + '.bin')

                # remove old files
                os.system("rm -rf " + self.path_database + version + '/samd20-xpro/' + version + '.bin_*')
                os.system("rm -rf " + self.path_database  + version + '/samd21-xpro/' + version + '.bin_*')

        files_samd20 = sorted(files_samd20)
        files_samd21 = sorted(files_samd21)
        versions = sorted(versions)

        return [files_samd20, files_samd21, versions]

    def database_files_riotboot(self):
        versions = []
        files_samd20 = []
        files_samd21 = []

        path_riotboot = self.path_database + "/riotboot/"
        database = os.listdir(path_riotboot)
        
        ### searching path for samd20 and samd21 ###
        for version in database:
            if os.path.isdir(os.path.join(path_riotboot, version)):
                # collection all versions
                versions.append(version)
                files_samd20.append(path_riotboot + version + '/samd20-xpro/' + version + '_slot0.bin')
                files_samd20.append(path_riotboot + version + '/samd20-xpro/' + version + '_slot1.bin')
                files_samd21.append(path_riotboot + version + '/samd21-xpro/' + version + '_slot0.bin')
                files_samd21.append(path_riotboot + version + '/samd21-xpro/' + version + '_slot1.bin')

                # remove old files
                os.system("rm -rf " + path_riotboot + version + '/samd20-xpro/' + version + '_slot0.bin_*')
                os.system("rm -rf " + path_riotboot  + version + '/samd21-xpro/' + version + '_slot1.bin_*')

        files_samd20 = sorted(files_samd20)
        files_samd21 = sorted(files_samd21)
        versions = sorted(versions)

        return [files_samd20, files_samd21, versions]

    def database_path_all_patches(self):
        path_samd20 = dict()
        path_samd21 = dict()
        path_samd20["normal"] = dict()
        path_samd20["riotboot"] = dict()
        path_samd21["normal"] = dict()
        path_samd21["riotboot"] = dict()

        path_normal = self.path_database + "algo_diffs/"
        path_riotboot = self.path_database + "algo_diffs_slots/"
        path_deltagen = self.path_database + "deltagen_diff/"
        algos_normal = os.listdir(path_normal)
        algos_normal = sorted(algos_normal)
        algos_riotboot = os.listdir(path_riotboot)
        algos_riotboot = sorted(algos_riotboot)

        ### searching path for samd20 and samd21 normal ###
        for algo in algos_normal:
            if os.path.isdir(os.path.join(path_normal, algo)):
                # collect all patches samd20
                files_samd20 = []
                path = path_normal + algo + "/samd20-xpro"
                files = os.listdir(path)
                files = sorted(files)
                for file in files:
                    files_samd20.append(os.path.join(path, file))
                # samd21
                files_samd21 = []
                path = path_normal + algo + "/samd21-xpro"
                files = os.listdir(path)
                files = sorted(files)
                for file in files:
                    files_samd21.append(os.path.join(path, file))
                path_samd20["normal"][algo] = files_samd20
                path_samd21["normal"][algo] = files_samd21
        # adding deltagen patches samd20
        files_deltagen = []
        path = path_deltagen + "data_basis/samd20-xpro"
        folders = os.listdir(path)
        files = []
        for folder in folders:
            content = os.listdir(os.path.join(path, folder))
            for file in content:
                if ".log" in file:
                    continue
                files.append(os.path.join(path, folder, file))
        files = sorted(files)
        path_samd20["normal"]["deltagen"] = files
        # samd21
        files_deltagen = []
        path = path_deltagen + "data_basis/samd20-xpro"
        folders = os.listdir(path)
        files = []
        for folder in folders:
            content = os.listdir(os.path.join(path, folder))
            for file in content:
                if ".log" in file:
                    continue
                files.append(os.path.join(path, folder, file))
        files = sorted(files)
        path_samd21["normal"]["deltagen"] = files

        ### searching path for samd20 and samd21 riotboot ###
        for algo in algos_riotboot:
            if os.path.isdir(os.path.join(path_riotboot, algo)):
                # collect all patches samd20
                files_samd20 = []
                path = path_riotboot + algo + "/samd20-xpro"
                files = os.listdir(path)
                files = sorted(files)
                for file in files:
                    files_samd20.append(os.path.join(path, file))
                # samd21
                files_samd21 = []
                path = path_riotboot + algo + "/samd21-xpro"
                files = os.listdir(path)
                files = sorted(files)
                for file in files:
                    files_samd21.append(os.path.join(path, file))
                path_samd20["riotboot"][algo] = files_samd20
                path_samd21["riotboot"][algo] = files_samd21
        # adding deltagen patches samd20
        files_deltagen = []
        path = path_deltagen + "data_basis/riotboot/samd20-xpro"
        folders = os.listdir(path)
        files = []
        for folder in folders:
            content = os.listdir(os.path.join(path, folder))
            for file in content:
                if ".log" in file:
                    continue
                files.append(os.path.join(path, folder, file))
        files = sorted(files)
        path_samd20["riotboot"]["deltagen"] = files
        # samd21
        files_deltagen = []
        path = path_deltagen + "data_basis/riotboot/samd21-xpro"
        folders = os.listdir(path)
        files = []
        for folder in folders:
            content = os.listdir(os.path.join(path, folder))
            for file in content:
                if ".log" in file:
                    continue
                files.append(os.path.join(path, folder, file))
        files = sorted(files)
        path_samd21["riotboot"]["deltagen"] = files

        return [path_samd20, path_samd21]
