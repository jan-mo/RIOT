
###
### builds the firmware for samd20 and samd21
### copies all data to database
###

# save current version in git stash
git status
echo ""
echo "Stash current git (necessary)? [y/N]"
read answer

if [ -z "$answer" ] || [ $answer != y ]
then
    echo "Stash is necessary!"
    exit
else
    git stash
    echo "Git was stashed!"
fi

echo "Enter firmware revision:"
read version

cd ../../../
git checkout thesis/${version}
cd firmwareExample

sudo make -j BOARD=samd20-xpro
sudo make -j BOARD=samd21-xpro

git diff thesis/rev_00 > firmware.diff

git checkout thesis/checking_firmware_versions

cd ../compareFirmware/database/scripts
./__copy_bin_elf.py ${version}
cd ../../
cd database/scripts

./__diff_previous.py ${version}
