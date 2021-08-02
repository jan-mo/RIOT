# save current version in git stash
git stash

cd ../..

echo Enter firmware version:
read version

path="compareFirmware/database/${version}/firmware.diff"

patch -p1 < $path
