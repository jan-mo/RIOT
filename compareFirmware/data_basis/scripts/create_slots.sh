
###
### generates and compiles riotboot for current revision with slot0 and slot1
###

# save current version in git stash
git status
echo ""
echo "Stash current git (necessary)? [y/N]"
read answer

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

cp ../riotboot/riotboot_patch.sh ../../../
git checkout thesis/${version}
cd ../../../

# update revision to add riotboot
./riotboot_patch.sh
rm riotboot_patch.sh
cd firmwareExample/
sudo rm -r bin/

sudo make -j BOARD=samd20-xpro
sudo make -j BOARD=samd21-xpro

# remove changes
git stash
git checkout thesis/checking_firmware_versions

# copy slots to revision folder
cd ../compareFirmware/data_basis
if [ -d riotboot/${version} ]
then
    echo "Directory riotboot/${version} exists. Overwrite!"
else
    mkdir riotboot/${version}
    mkdir riotboot/${version}/samd20-xpro
    mkdir riotboot/${version}/samd21-xpro
fi

cp ../../firmwareExample/bin/samd20-xpro/firmware_example-slot0.bin ./riotboot/${version}/samd20-xpro/${version}_slot0.bin
cp ../../firmwareExample/bin/samd20-xpro/firmware_example-slot1.bin ./riotboot/${version}/samd20-xpro/${version}_slot1.bin
cp ../../firmwareExample/bin/samd21-xpro/firmware_example-slot0.bin ./riotboot/${version}/samd21-xpro/${version}_slot0.bin
cp ../../firmwareExample/bin/samd21-xpro/firmware_example-slot1.bin ./riotboot/${version}/samd21-xpro/${version}_slot1.bin

echo Done!
