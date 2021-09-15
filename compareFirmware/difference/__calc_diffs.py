#!/usr/bin/env python3.9

import os

# parallel processing
from pathos.multiprocessing import ProcessingPool as Pool
from pathos.helpers import mp as helper


class calcDiff:

    def __init__(self, source, restore, diff_algos):
        self.folder = source
        self.folder_restore = restore
        self.diff_algos = diff_algos

    ### calculate all differences ###
    def second_loop(self, i, file1, files, sizes, name_arch):
        # getting PID
        pid = helper.current_process().pid
        print(name_arch + " differences of Rev_" + str(i).zfill(2) + " PID:" + str(pid))

        for j, file2 in enumerate(files):

            #### diff ####
            if "diff" in self.diff_algos:
                name_diff = "diff_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_diff = self.folder + "diff/" + name_arch + "/" + name_diff
                restore_diff = self.folder_restore + name_diff
                # diff file
                os.system("diff -a " + file1 + " " + file2 + " > " + patch_diff)
                # patch file
                os.system("cp " + file1 + " " + restore_diff)
                os.system("patch --quiet " + restore_diff + " " + patch_diff)

            #### bsdiff ####
            if "bsdiff" in self.diff_algos:
                name_bsdiff = "bsdiff_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_bsdiff = self.folder + "bsdiff/" + name_arch + "/" + name_bsdiff
                restore_bsdiff = self.folder_restore + name_bsdiff
                # diff file
                os.system("bsdiff " + file1 + " " + file2 + " " + patch_bsdiff)
                # patch file
                os.system("bspatch " + file1 + " " + restore_bsdiff + " " + patch_bsdiff)

            #### xdelta3 ####
            if "xdelta3" in self.diff_algos:
                name_xdelta3 = "xdelta3_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_xdelta3 = self.folder + "xdelta3/" + name_arch + "/" + name_xdelta3
                restore_xdelta3 = self.folder_restore + name_xdelta3
                # diff file
                os.system("xdelta3 -e -S -N -D -R -s " + file1 + " " + file2 + " " + patch_xdelta3)
                # patch file
                os.system("xdelta3 -d -s " + file1 + " " + patch_xdelta3 + " " + restore_xdelta3)

            #### bdelta ####
            if "bdelta" in self.diff_algos:
                name_bdelta = "bdelta_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_bdelta = self.folder + "bdelta/" + name_arch + "/" + name_bdelta
                restore_bdelta = self.folder_restore + name_bsdiff
                # diff file
                print("bdelta " + file1 + " " + file2 + " " + patch_bdelta)
                os.system("bdelta " + file1 + " " + file2 + " " + patch_bdelta)
                # patch file
                print("bpatch " + file1 + " " + restore_bdelta + " " + patch_bdelta)
                os.system("bpatch " + file1 + " " + restore_bdelta + " " + patch_bdelta)

            #### rsync8 ####
            if "rsync8" in self.diff_algos:
                name_rsync8 = "rsync8_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_rsync8 = self.folder + "rsync8/" + name_arch + "/" + name_rsync8
                restore_rsync8 = self.folder_restore + name_rsync8
                rsync8_par = "_rsync8_" + str(pid)      # save file for parallel loop
                # diff file
                os.system("cp " + file1 + " " + file1 + rsync8_par)
                if i != j :
                    os.system("cp " + file2 + " " + file2 + rsync8_par)
                os.system("rsync -arvq -B=8 --only-write-batch=" + patch_rsync8 + " " + file2 + rsync8_par + " " + file1 + rsync8_par)
                # patch file
                os.system("rsync -arvq -B=8 --read-batch=" + patch_rsync8 + " " + file1 + rsync8_par)
                os.system("mv " + file1 + rsync8_par + " " + restore_rsync8)
                if i != j:
                    os.system("rm " + file2 + rsync8_par)

            #### rsync16 ####
            if "rsync16" in self.diff_algos:
                name_rsync16 = "rsync16_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_rsync16 = self.folder + "rsync16/" + name_arch + "/" + name_rsync16
                restore_rsync16 = self.folder_restore + name_rsync16
                rsync16_par = "_rsync16_" + str(pid)    # save file for parallel loop
                # diff file
                os.system("cp " + file1 + " " + file1 + rsync16_par)
                if i != j:
                    os.system("cp " + file2 + " " + file2 + rsync16_par)
                os.system("rsync -arvq -B=16 --only-write-batch=" + patch_rsync16 + " " + file2 + rsync16_par + " " + file1 + rsync16_par)
                # patch file
                os.system("rsync -arvq -B=16 --read-batch=" + patch_rsync16 + " " + file1 + rsync16_par)
                os.system("mv " + file1 + rsync16_par + " " + restore_rsync16)
                if i != j:
                    os.system("rm " + file2 + rsync16_par)

            #### rsync32 ####
            if "rsync32" in self.diff_algos:
                name_rsync32 = "rsync32_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_rsync32 = self.folder + "rsync32/" + name_arch + "/" + name_rsync32
                restore_rsync32 = self.folder_restore + name_rsync32
                rsync32_par = "_rsync32_" + str(pid)    # save file for parallel loop
                # diff file
                os.system("cp " + file1 + " " + file1 + rsync32_par)
                if i != j:
                    os.system("cp " + file2 + " " + file2 + rsync32_par)
                os.system("rsync -arvq -B=32 --only-write-batch=" + patch_rsync32 + " " + file2 + rsync32_par + " " + file1 + rsync32_par)
                # patch file
                os.system("rsync -arvq -B=32 --read-batch=" + patch_rsync32 + " " + file1 + rsync32_par)
                os.system("mv " + file1 + rsync32_par + " " + restore_rsync32)
                if i != j:
                    os.system("rm " + file2 + rsync32_par)

            ### detools no compression ###
            if "detools_none" in self.diff_algos:
                name_detools_none = "detools_none_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
                patch_detools_none = self.folder + "detools_none/" + name_arch + "/" + name_detools_none
                restore_detools_none = self.folder_restore + name_detools_none
                # diff file
                os.system("python -m detools create_patch -c none -t hdiffpatch -a hdiffpatch "  + file1 + " " + file2 + " " + patch_detools_none + " > silent")
                # patch file
                os.system("python -m detools apply_patch "  + file1 + " " + patch_detools_none + " " + restore_detools_none + " > silent")
                os.system("rm -f silent")

            ### detools heatshrink compression ###
            if "detools_heat" in self.diff_algos:
                name_detools_heat = "detools_heat_rev_" + str(i).zfill(2) + "_rev_" + str(j).zfill(2)
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

            if "bsdiff" in self.diff_algos:
                sizes["bsdiff"][name_bsdiff] = {"size":os.path.getsize(patch_bsdiff),
                                                "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_bsdiff) else "fail",
                                                "normalized":os.path.getsize(patch_bsdiff)/os.path.getsize(file2)}

            if "xdelta3" in self.diff_algos:
                sizes["xdelta3"][name_xdelta3] = {"size":os.path.getsize(patch_xdelta3),
                                                  "check":"pass" if os.path.getsize(file2) == os.path.getsize(restore_xdelta3) else "fail",
                                                  "normalized":os.path.getsize(patch_xdelta3)/os.path.getsize(file2)}

            if "bdelta" in self.diff_algos:
                sizes["bdelta"][name_bdelta] = os.path.getsize(folder + name_bdelta)

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
        num = []
        file1 = []
        files = []
        sizes = []
        arch = []
        for i, file in enumerate(files_all):
            num.append(i)
            file1.append(file)
            files.append(files_all)
            sizes.append(sizes_all)
            arch.append(name_MCU)

        result_pool = Pool().amap(self.second_loop, num, file1, files, sizes, arch)

        return result_pool.get()
