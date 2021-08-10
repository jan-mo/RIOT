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
cd -
./__copy_bin_elf.py ${version}
