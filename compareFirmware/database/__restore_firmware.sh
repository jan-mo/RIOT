# save current version in git stash
echo "Stash current git? [y/N]"
read answer

if [ -z "$answer" ] || [ $answer != y ]
then
    echo No stash.
else
	git stash
	echo Git was stashed!
fi

cd ../..

echo Enter firmware version:
read version

path="compareFirmware/database/${version}/firmware.diff"

patch -p1 < $path
