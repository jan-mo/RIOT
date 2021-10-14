
###
### builds the firmware for samd20 and samd21
### copies all data to database
###

# save current version in git stash
git status
echo ""
echo "Stash current git (necessary)? [y/N]" && read answer

# ignore git stash, for DEBUGGING ONLY !!!
if [ -z "$answer" ]
then
    echo "Stash is necessary!"
    exit

elif [ $answer == ignore ]
then
    echo "Stash is necessary!"
    echo "Ignored for DEBUGGING, checkout firmwareExample is not possible!"

elif [ $answer == y ]
then
    git stash
    echo "Git was stashed!"

else
    echo "Stash is necessary!"
    exit
fi

echo "Enter firmware revision:"
read version

# check revision exists
cd ../
[ -d ${version} ] && echo "Directory ${version} exists." && echo "Continue? [y/N]" && read input && [ -z "$input" ] || [ $input != y ] && exit

cd ../../
git checkout thesis/${version}
cd firmwareExample

sudo make -j BOARD=samd20-xpro
sudo make -j BOARD=samd21-xpro

git diff thesis/rev_00 > firmware.diff

git checkout thesis/checking_firmware_versions

cd ../compareFirmware/data_basis/scripts
./__copy_bin_elf.py ${version}

cd ../scripts
./__diff_previous.py

cd ../scripts
