
# saving revision information to file
git tag -n thesis/rev* > revision_tags.txt

# saving size of revision bin-files
echo "SAMD20 bin sizes [Byte]:" > revision_bin_sizes.txt
du -ab --max-depth=3 | sort -k 2| grep bin | grep rev | grep samd20 >> revision_bin_sizes.txt
echo "" >> revision_bin_sizes.txt
echo "SAMD21 bin sizes [Byte]:" >> revision_bin_sizes.txt
du -ab --max-depth=3 | sort -k 2 | grep bin | grep rev | grep samd21 >> revision_bin_sizes.txt
