#!/usr/bin/env python3.9

import os

# parallel processing
from pathos.multiprocessing import ProcessingPool as Pool
from pathos.helpers import mp as helper

###
### creates a class calcDiff to calculate all differences in given files
### in __init__ diff_algos, source folder and restore folder are set
###

class calcDiff:

    def __init__(self, source, restore, diff_algos, git_folder):
        self.folder = source
        self.folder_restore = restore
        self.diff_algos = diff_algos
        self.git_folder = git_folder

    ### calculate all differences ###
    def second_loop(self, file1, files, sizes, name_arch):
        # getting PID
        pid = helper.current_process().pid

        split_file1 = file1.split("/")
        split_file1 = split_file1[-1].split(".")
        name_file1 = split_file1[0]
        rev_file1 = split_file1[0].split("_")
        rev_file1 = rev_file1[1]

        print(name_arch + " differences of Rev_" + rev_file1 + " PID:" + str(pid) + " File:" + file1)

        for file2 in files:

            split_file2 = file2.split("/")
            split_file2 = split_file2[-1].split(".")
            name_file2 = split_file2[0]
            rev_file2 = split_file2[0].split("_")
            rev_file2 = rev_file2[1]

            #### diff ####
            if "diff" in self.diff_algos:
                name_diff = "diff_" + name_file1 + "_" + name_file2
                patch_diff = self.folder + "diff/" + name_arch + "/" + name_diff
                restore_diff = self.folder_restore + name_diff
                # diff file
                os.system("diff -a " + file1 + " " + file2 + " > " + patch_diff)
                # patch file
                os.system("cp " + file1 + " " + restore_diff)
                os.system("patch --quiet " + restore_diff + " " + patch_diff)

            #### byte_diff ####
            if "byte_diff" in self.diff_algos:
                name_byte_diff = "byte_diff_" + name_file1 + "_" + name_file2
                patch_byte_diff = self.folder + "byte_diff/" + name_arch + "/" + name_byte_diff
                restore_byte_diff = self.folder_restore + name_byte_diff
                # converted files
                path_conv_file1 = "../../matches_diff/converted_bins/" + name_arch + "/" + name_file1 + ".bin_conv"
                path_conv_file2 = "../../matches_diff/converted_bins/" + name_arch + "/" + name_file2 + ".bin_conv"
                # diff file
                os.system("diff -a " + path_conv_file1 + " " + path_conv_file2 + " > " + patch_byte_diff)
                # patch file
                os.system("cp " + path_conv_file1 + " " + restore_byte_diff)
                os.system("patch --quiet " + restore_byte_diff + " " + patch_byte_diff)

            #### baseline ####
            if "baseline" in self.diff_algos:
                name_baseline = "baseline" + name_file1 + "_" + name_file2
                patch_baseline = self.folder + "baseline/" + name_arch + "/" + name_baseline
                restore_baseline = self.folder_restore + name_baseline
                # converted files
                path_conv_file1 = "../../matches_diff/converted_bins/" + name_arch + "/" + name_file1 + ".bin_conv"
                path_conv_file2 = "../../matches_diff/converted_bins/" + name_arch + "/" + name_file2 + ".bin_conv"
                # diff file
                os.system("diff -a " + path_conv_file1 + " " + path_conv_file2 + " > " + patch_baseline)
                # patch file
                os.system("cp " + path_conv_file1 + " " + restore_baseline)
                os.system("patch --quiet " + restore_baseline + " " + patch_baseline)
                # save patch byte diff, only added bytes
                os.system("grep \"^>\" " + patch_baseline + " > " + patch_baseline + "_added_bytes")

            #### bsdiff ####
            if "bsdiff" in self.diff_algos:
                name_bsdiff = "bsdiff_" + name_file1 + "_" + name_file2
                patch_bsdiff = self.folder + "bsdiff/" + name_arch + "/" + name_bsdiff
                restore_bsdiff = self.folder_restore + name_bsdiff
                # diff file
                os.system("bsdiff " + file1 + " " + file2 + " " + patch_bsdiff)
                # patch file
                os.system("bspatch " + file1 + " " + restore_bsdiff + " " + patch_bsdiff)

            #### xdelta3 ####
            if "xdelta3" in self.diff_algos:
                name_xdelta3 = "xdelta3_" + name_file1 + "_" + name_file2
                patch_xdelta3 = self.folder + "xdelta3/" + name_arch + "/" + name_xdelta3
                restore_xdelta3 = self.folder_restore + name_xdelta3
                # diff file
                os.system("xdelta3 -e -S -N -D -R -s " + file1 + " " + file2 + " " + patch_xdelta3)
                # patch file
                os.system("xdelta3 -d -s " + file1 + " " + patch_xdelta3 + " " + restore_xdelta3)

            #### zdelta ####
            if "zdelta" in self.diff_algos:
                name_zdelta = "zdelta_" + name_file1 + "_" + name_file2
                patch_zdelta = self.folder + "zdelta/" + name_arch + "/" + name_zdelta
                restore_zdelta = self.folder_restore + name_zdelta
                ### make sure zdelta is installed!!!!
                zdelta_path = "./" + self.git_folder + "zdelta/"
                # diff file
                os.system(zdelta_path + "zdc " + file1 + " " + file2 + " " + patch_zdelta)
                # patch file
                os.system(zdelta_path + "zdu " + file1 + " " + patch_zdelta + " " + restore_zdelta)

            #### vcdiff ####
            if "vcdiff" in self.diff_algos:
                name_vcdiff = "vcdiff_" + name_file1 + "_" + name_file2
                patch_vcdiff = self.folder + "vcdiff/" + name_arch + "/" + name_vcdiff
                restore_vcdiff = self.folder_restore + name_bsdiff
                ### make sure zdelta is installed!!!!
                vcdiff_path = "./" + self.git_folder + "vcdiff/"
                # diff file
                os.system(vcdiff_path + "vcdiff encode -dictionary " + file1 + " < " + file2 + " > " + patch_vcdiff)
                # patch file
                os.system(vcdiff_path + "vcdiff decode -dictionary " + file1 + " < " + patch_vcdiff + " > " + restore_vcdiff)

            #### rsync8 ####
            if "rsync8" in self.diff_algos:
                name_rsync8 = "rsync8_" + name_file1 + "_" + name_file2
                patch_rsync8 = self.folder + "rsync8/" + name_arch + "/" + name_rsync8
                restore_rsync8 = self.folder_restore + name_rsync8
                rsync8_par = "_rsync8_" + str(pid)      # save file for parallel loop
                # diff file
                os.system("cp " + file1 + " " + file1 + rsync8_par)
                if rev_file1 != rev_file2:
                    os.system("cp " + file2 + " " + file2 + rsync8_par)
                os.system("rsync -arvq -B=8 --only-write-batch=" + patch_rsync8 + " " + file2 + rsync8_par + " " + file1 + rsync8_par)
                # patch file
                os.system("rsync -arvq -B=8 --read-batch=" + patch_rsync8 + " " + file1 + rsync8_par)
                os.system("mv " + file1 + rsync8_par + " " + restore_rsync8)
                # clear old save files
                os.system("rm -f " + file1 + rsync8_par)
                os.system("rm -f " + file2 + rsync8_par)

            #### rsync16 ####
            if "rsync16" in self.diff_algos:
                name_rsync16 = "rsync16_" + name_file1 + "_" + name_file2
                patch_rsync16 = self.folder + "rsync16/" + name_arch + "/" + name_rsync16
                restore_rsync16 = self.folder_restore + name_rsync16
                rsync16_par = "_rsync16_" + str(pid)    # save file for parallel loop
                # diff file
                os.system("cp " + file1 + " " + file1 + rsync16_par)
                if rev_file1 != rev_file2:
                    os.system("cp " + file2 + " " + file2 + rsync16_par)
                os.system("rsync -arvq -B=16 --only-write-batch=" + patch_rsync16 + " " + file2 + rsync16_par + " " + file1 + rsync16_par)
                # patch file
                os.system("rsync -arvq -B=16 --read-batch=" + patch_rsync16 + " " + file1 + rsync16_par)
                os.system("mv " + file1 + rsync16_par + " " + restore_rsync16)
                # clear old save files
                os.system("rm -f " + file1 + rsync16_par)
                os.system("rm -f " + file2 + rsync16_par)

            #### rsync32 ####
            if "rsync32" in self.diff_algos:
                name_rsync32 = "rsync32_" + name_file1 + "_" + name_file2
                patch_rsync32 = self.folder + "rsync32/" + name_arch + "/" + name_rsync32
                restore_rsync32 = self.folder_restore + name_rsync32
                rsync32_par = "_rsync32_" + str(pid)    # save file for parallel loop
                # diff file
                os.system("cp " + file1 + " " + file1 + rsync32_par)
                if rev_file1 != rev_file2:
                    os.system("cp " + file2 + " " + file2 + rsync32_par)
                os.system("rsync -arvq -B=32 --only-write-batch=" + patch_rsync32 + " " + file2 + rsync32_par + " " + file1 + rsync32_par)
                # patch file
                os.system("rsync -arvq -B=32 --read-batch=" + patch_rsync32 + " " + file1 + rsync32_par)
                os.system("mv " + file1 + rsync32_par + " " + restore_rsync32)
                # clear old save files
                os.system("rm -f " + file1 + rsync32_par)
                os.system("rm -f " + file2 + rsync32_par)

            ### detools no compression ###
            if "detools_none" in self.diff_algos:
                name_detools_none = "detools_none_" + name_file1 + "_" + name_file2
                patch_detools_none = self.folder + "detools_none/" + name_arch + "/" + name_detools_none
                restore_detools_none = self.folder_restore + name_detools_none
                # diff file
                os.system("python -m detools create_patch -c none -t hdiffpatch -a hdiffpatch "  + file1 + " " + file2 + " " + patch_detools_none + " > silent")
                # patch file
                os.system("python -m detools apply_patch "  + file1 + " " + patch_detools_none + " " + restore_detools_none + " > silent")
                os.system("rm -f silent")

            ### detools heatshrink compression ###
            if "detools_heat" in self.diff_algos:
                name_detools_heat = "detools_heat_" + name_file1 + "_" + name_file2
                patch_detools_heat = self.folder + "detools_heat/" + name_arch + "/" + name_detools_heat
                restore_detools_heat = self.folder_restore + name_detools_heat
                # diff file
                os.system("python -m detools create_patch -a bsdiff -c heatshrink  "  + file1 + " " + file2 + " " + patch_detools_heat + " > silent")
                # patch file
                os.system("python -m detools apply_patch "  + file1 + " " + patch_detools_heat + " " + restore_detools_heat + " > silent")
                os.system("rm -f silent")


            #### check patch and calc sizes ####
            if "diff" in self.diff_algos:
                sizes["diff"][name_diff] = {"size":os.path.getsize(patch_diff),
                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_diff) else "fail",
                                            "normalized":os.path.getsize(patch_diff)/os.path.getsize(file2)}

            if "byte_diff" in self.diff_algos:
                sizes["byte_diff"][name_byte_diff] = {"size":os.path.getsize(patch_byte_diff),
                                                      "check":"pass" if os.path.getsize(path_conv_file2) == os.path.getsize(restore_byte_diff) else "fail",
                                                      "normalized":os.path.getsize(patch_byte_diff)/os.path.getsize(path_conv_file2)}

            if "baseline" in self.diff_algos:
                sizes["baseline"][name_baseline] = {"size":sum(1 for line in open(patch_baseline + "_added_bytes")),
                                                    "check":"pass" if os.path.getsize(path_conv_file2) == os.path.getsize(restore_baseline) else "fail",
                                                    "normalized":sum(1 for line in open(patch_baseline + "_added_bytes"))/os.path.getsize(path_conv_file2)}

            if "bsdiff" in self.diff_algos:
                sizes["bsdiff"][name_bsdiff] = {"size":os.path.getsize(patch_bsdiff),
                                                "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_bsdiff) else "fail",
                                                "normalized":os.path.getsize(patch_bsdiff)/os.path.getsize(file2)}

            if "xdelta3" in self.diff_algos:
                sizes["xdelta3"][name_xdelta3] = {"size":os.path.getsize(patch_xdelta3),
                                                  "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_xdelta3) else "fail",
                                                  "normalized":os.path.getsize(patch_xdelta3)/os.path.getsize(file2)}

            if "zdelta" in self.diff_algos:
                sizes["zdelta"][name_zdelta] = {"size":os.path.getsize(patch_zdelta),
                                                  "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_zdelta) else "fail",
                                                  "normalized":os.path.getsize(patch_zdelta)/os.path.getsize(file2)}

            if "vcdiff" in self.diff_algos:
                sizes["vcdiff"][name_vcdiff] = {"size":os.path.getsize(patch_vcdiff),
                                                  "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_vcdiff) else "fail",
                                                  "normalized":os.path.getsize(patch_vcdiff)/os.path.getsize(file2)}

            if "rsync8" in self.diff_algos:
                sizes["rsync8"][name_rsync8] = {"size":os.path.getsize(patch_rsync8),
                                                "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_rsync8) else "fail",
                                                "normalized":os.path.getsize(patch_rsync8)/os.path.getsize(file2)}

            if "rsync16" in self.diff_algos:        
                sizes["rsync16"][name_rsync16] = {"size":os.path.getsize(patch_rsync16),
                                                  "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_rsync16) else "fail",
                                                  "normalized":os.path.getsize(patch_rsync16)/os.path.getsize(file2)}

            if "rsync32" in self.diff_algos:        
                sizes["rsync32"][name_rsync32] = {"size":os.path.getsize(patch_rsync32),
                                                  "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_rsync32) else "fail",
                                                  "normalized":os.path.getsize(patch_rsync32)/os.path.getsize(file2)}

            if "detools_none" in self.diff_algos:
                sizes["detools_none"][name_detools_none] = {"size":os.path.getsize(patch_detools_none),
                                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_detools_none) else "fail",
                                                            "normalized":os.path.getsize(patch_detools_none)/os.path.getsize(file2)}

            if "detools_heat" in self.diff_algos:
                sizes["detools_heat"][name_detools_heat] = {"size":os.path.getsize(patch_detools_heat),
                                                            "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_detools_heat) else "fail",
                                                            "normalized":os.path.getsize(patch_detools_heat)/os.path.getsize(file2)}
        return [sizes]


    ### calculates the differences between files
    def calc_diffs(self, files_all, sizes_all, name_MCU):
        file1 = []
        files = []
        sizes = []
        arch = []
        for file in files_all:
            file1.append(file)
            files.append(files_all)
            sizes.append(sizes_all)
            arch.append(name_MCU)

        result_pool = Pool().amap(self.second_loop, file1, files, sizes, arch)

        return result_pool.get()


    ### calculates the differences between files of slot0 and slot1, with alternating the slots
    def calc_diffs_slots_alternating(self, files_slot0, files_slot1, sizes_all, name_MCU):
        file1 = []
        files = []
        sizes = []
        arch = []
        # updating from slot0 to slot1
        # files_slot0 holds every even revision
        length = len(files_slot0)
        # check same length for both slots
        if length > len(files_slot1)-1:
            length = length -1
        for i in range(length):
            file1.append(files_slot0[i])
            files.append([files_slot1[i]])
            sizes.append(sizes_all)
            arch.append(name_MCU)

        # updating from slot1 to slot0
        # files_slot1 holds every odd revision
        length = len(files_slot1)-1
        # check same length for both slots
        if length < len(files_slot0)-1:
            length = length + 1
        for i in range(length):
            file1.append(files_slot1[i])
            files.append([files_slot0[i+1]])
            sizes.append(sizes_all)
            arch.append(name_MCU)

        result_pool = Pool().amap(self.second_loop, file1, files, sizes, arch)

        return result_pool.get()


    ### calculates the differences between files of same slot (second upper diagonal)
    def calc_diffs_slots_same(self, files_slot0, files_slot1, sizes_all, name_MCU):
        file1 = []
        files = []
        sizes = []
        arch = []
        # updating from slot0 to slot0
        # files_slot0 holds every even revision
        for i in range(len(files_slot0)-1):
            file1.append(files_slot0[i])
            files.append([files_slot0[i+1]])
            sizes.append(sizes_all)
            arch.append(name_MCU)

        # updating from slot1 to slot1
        # files_slot1 holds every odd revision
        for i in range(len(files_slot1)-1):
            file1.append(files_slot1[i])
            files.append([files_slot1[i+1]])
            sizes.append(sizes_all)
            arch.append(name_MCU)

        result_pool = Pool().amap(self.second_loop, file1, files, sizes, arch)

        return result_pool.get()
