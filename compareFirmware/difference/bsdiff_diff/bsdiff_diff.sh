echo Hint: Give both firmwareversions as arguments!

echo run/clear:
read command

if [ $command = clear ]; then
    rm diff_bin_samd20 diff_bin_samd21
    echo Cleared!
    exit
fi

if [ $command != run ]; then
    echo Wrong command!
    exit
fi

if [ $command = run ] || [ $command = all ]; then
    # samd20-xpro
    bsdiff "../../database/${1}/samd20-xpro/${1}.bin" "../../database/${2}/samd20-xpro/${2}.bin" diff_bin_samd20

    echo Bytes: $(ls -la diff_bin_samd20)

    cp diff_bin_samd20 "samd20-xpro/bin_${1}__${2}"

    # samd21-xpro
    bsdiff "../../database/${1}/samd21-xpro/${1}.bin" "../../database/${2}/samd21-xpro/${2}.bin" diff_bin_samd21

    echo Bytes: $(ls -la diff_bin_samd21)

    cp diff_bin_samd21 "samd21-xpro/bin_${1}__${2}"
fi

rm diff_bin_samd20 diff_bin_samd21

echo Hint: diff can be reverted with bspatch.
echo Done!
