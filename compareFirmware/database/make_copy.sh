# save current version in git stash
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

git checkout thesis/${version}
cd ../../firmwareExample/

sudo make -j BOARD=samd20-xpro
sudo make -j BOARD=samd21-xpro

git diff thesis/rev_00 > firmware.diff
size = $(wc -c < firmware.diff)

if [ $size >= 6000000 ]
then
	split -b50M firmware.diff firmware.diff_split_
	rm firmware.diff
fi

git checkout thesis/checking_firmware_versions

cd -
./__copy_bin_elf.py ${version}
cd ../database
