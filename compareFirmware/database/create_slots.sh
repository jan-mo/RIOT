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

cp riotboot_patch.sh ../../
git checkout thesis/${version}
cd ../../

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
cd ../compareFirmware/database
mkdir riotboot/${version}
mkdir riotboot/${version}/samd20-xpro
mkdir riotboot/${version}/samd21-xpro
cp ../../firmwareExample/bin/samd20-xpro/firmware_example-slot0.bin ./riotboot/${version}/samd20-xpro/${version}_slot0.bin
cp ../../firmwareExample/bin/samd20-xpro/firmware_example-slot1.bin ./riotboot/${version}/samd20-xpro/${version}_slot1.bin
cp ../../firmwareExample/bin/samd21-xpro/firmware_example-slot0.bin ./riotboot/${version}/samd21-xpro/${version}_slot0.bin
cp ../../firmwareExample/bin/samd21-xpro/firmware_example-slot1.bin ./riotboot/${version}/samd21-xpro/${version}_slot1.bin

echo Done!
