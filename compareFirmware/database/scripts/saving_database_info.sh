
###
### saves revision information from database
### saves the sizes of all revisions
###

# saving revision information to file
cd ..
git fetch --tags -f
git tag -n thesis/rev* > output/revision_tags.txt

# saving size of revision bin-files
echo "SAMD20 bin sizes [Byte]:" > output/revision_bin_sizes.txt
du -ab --max-depth=3 | sort -k 2| grep bin | grep rev | grep samd20 >> output/revision_bin_sizes.txt
echo "" >> output/revision_bin_sizes.txt
echo "SAMD21 bin sizes [Byte]:" >> output/revision_bin_sizes.txt
du -ab --max-depth=3 | sort -k 2 | grep bin | grep rev | grep samd21 >> output/revision_bin_sizes.txt
