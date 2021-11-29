#!/usr/bin/env python3.9

import sys


if len(sys.argv) == 1:
    print("No argument given")
    exit()

file = sys.argv[1]

with open(file, 'rb') as f:
    data_hex = f.read().hex()
new_data = "{"
count = 0
for idx in range(0,len(data_hex),2):
    if idx == len(data_hex)-2:
        new_data = new_data + hex(int(data_hex[idx:idx+2], base=16)) + "};"
    else:
        new_data = new_data + hex(int(data_hex[idx:idx+2], base=16)) + ", "
    count = count + 1
    if count % 16 == 0:
        new_data = new_data + "\n"

with open("output_convert", 'w') as out:
    out.write(new_data)

print(new_data)
print("Count ", count)
