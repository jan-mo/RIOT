cd ../firmware_example/
sudo make -j BOARD=samd20-xpro
sudo make -j BOARD=samd21-xpro
git diff thesis/rev_00 ../firmware_example/ > firmware.diff
cd -
./__copy_bin_elf.py
