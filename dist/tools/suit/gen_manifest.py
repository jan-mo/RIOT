#!/usr/bin/env python3

#
# Copyright (C) 2019 Inria
#               2019 FU Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.
#

import argparse
import json
import os
import uuid


def str2int(x):
    if x.startswith("0x"):
        return int(x, 16)
    else:
        return int(x)


def parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--urlroot', '-u', help='',
                        default="coap://example.org")
    parser.add_argument('--seqnr', '-s', default=0,
                        help='Sequence number of the manifest')
    parser.add_argument('--output', '-o', default="out.json",
                        help='Manifest output binary file path')
    parser.add_argument('--uuid-vendor', '-V', default="riot-os.org",
                        help='Manifest vendor uuid')
    parser.add_argument('--uuid-class', '-C', default="native",
                        help='Manifest class uuid')
    parser.add_argument('slotfiles', nargs="+",
                        help='The list of slot file paths')
    return parser.parse_args()


def main(args):
    uuid_vendor = uuid.uuid5(uuid.NAMESPACE_DNS, args.uuid_vendor)
    uuid_class = uuid.uuid5(uuid_vendor, args.uuid_class)

    template = {}

    template["manifest-version"] = int(1)
    template["manifest-sequence-number"] = int(args.seqnr)

    images = []
    for filename_offset in args.slotfiles:
        comp_name = ["00"]
        split = filename_offset.split(":", maxsplit=2)
        if len(split) == 1:
            filename, offset = split[0], 0
        elif len(split) == 2:
            filename, offset = split[0], str2int(split[1])
        else:
            filename, offset, comp_name = split[0], str2int(split[1]), split[2].split(":")

        images.append((filename, offset, comp_name))

    template["components"] = []

    for slot, image in enumerate(images):
        filename, offset, comp_name = image

        uri = os.path.join(args.urlroot, os.path.basename(filename))

        component = {
            "install-id": comp_name,
            "vendor-id": uuid_vendor.hex,
            "class-id": uuid_class.hex,
            "file": filename,
            "uri": uri,
            "bootable": False,
            "compression": "minidiff", #"bsdiff",
        }

        if component["compression"] == "bsdiff" or component["compression"] == "minidiff":
            print(component["compression"])

            # calc prev and current fw version
            split_file = filename.split("/")
            file = split_file[-1]
            # create path
            path = ""
            path_GIT = ""
            for elem in split_file[:-1]:
                path = path + elem + "/"
                if "GIT" not in path_GIT:
                    path_GIT = path_GIT + elem + "/"
            # find fw version
            fw_versions = os.listdir(path)
            fw_versions.sort()
            fw_old_slot0 = ""
            fw_old_slot1 = ""
            for version in fw_versions:
                if "slot0_old" == version:
                    fw_old_slot0 = version
                elif "slot1_old" == version:
                    fw_old_slot1 = version
            # check older fw version
            if fw_old_slot0 == "":
                print("No old file detected, publish again!")
                if "slot0" in file:
                    os.system("cp " + filename + " " + path + "slot0_old")
                elif "slot1" in file:
                    os.system("cp " + filename + " " + path + "slot1_old")
            elif fw_old_slot1 == "":
                print("No old file detected, publish again!")
                if "slot0" in file:
                    os.system("cp " + filename + " " + path + "slot0_old")
                elif "slot1" in file:
                    os.system("cp " + filename + " " + path + "slot1_old")
            else:
                if "slot0" in file:
                    curr_fw = file
                    prev_fw = fw_old_slot1
                elif "slot1" in file:
                    curr_fw = file
                    prev_fw = fw_old_slot0

                print("curr: ", file)
                print("prev: ", prev_fw)

                # save current fw
                if "slot0" in file:
                    os.system("cp " + filename + " " + path + "slot0_old_save")
                elif "slot1" in file:
                    os.system("cp " + filename + " " + path + "slot1_old_save")

                # calc bsdiff patch
                file1 = path_GIT + "RIOT/examples/suit_update/bin/samd21-xpro/" + curr_fw
                file2 = path_GIT + "RIOT/examples/suit_update/bin/samd21-xpro/" + prev_fw
                if component["compression"] == "bsdiff":
                    os.system(path_GIT + "bsdiff/bsdiff " + file1 + " " + file2 + " " + filename)
                elif component["compression"] == "minidiff":
                    os.system(path_GIT + "RIOT/minidiff.py " + file1 + " " + file2 + " " + filename + " " + path_GIT)

                # update old fw file
                if "slot0" in file:
                    os.system("cp " + path + "slot0_old_save" + " " + path + "slot0_old")
                elif "slot1" in file:
                    os.system("cp " + path + "slot1_old_save" + " " + path + "slot1_old")

        if offset:
            component.update({"offset": offset})

        template["components"].append(component)

    with open(args.output, 'w') as f:
        json.dump(template, f, indent=4)


if __name__ == "__main__":
    _args = parse_arguments()
    main(_args)
