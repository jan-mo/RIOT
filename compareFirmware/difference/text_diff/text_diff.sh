echo Hint: Give both firmwareversions as arguments!
echo Hint: Uses xxd for \'bin\', objdump for \'elf\' and diff for \'map\'.

echo bin/elf/map/all/clear:
read command

if [ $command = clear ]; then
    rm diff_bin_samd20 diff_bin_samd21
    rm diff_elf_samd20 diff_elf_samd21
    rm diff_map_samd20 diff_map_samd21
    echo Cleared!
    exit
fi


if [ $command != bin ] && [ $command != elf ] && [ $command != map ] && [ $command != all ]; then
    echo Wrong command!
    exit
fi

if [ $command = bin ] || [ $command = all ]; then
    # samd20-xpro
    xxd "../../database/${1}/samd20-xpro/${1}.bin" > out1
    xxd "../../database/${2}/samd20-xpro/${2}.bin" > out2

    diff -a out1 out2 > diff_bin_samd20
    echo Lines: $(wc -l diff_bin_samd20)

    cp diff_bin_samd20 "samd20-xpro/bin_${1}__${2}"

    # samd21-xpro
    xxd "../../database/${1}/samd21-xpro/${1}.bin" > out1
    xxd "../../database/${2}/samd21-xpro/${2}.bin" > out2

    diff -a out1 out2 > diff_bin_samd21
    echo Lines: $(wc -l diff_bin_samd21)

    cp diff_bin_samd21 "samd21-xpro/bin_${1}__${2}"
fi

if [ $command = elf ] || [ $command = all ]; then
    # samd20-xpro
    arm-none-eabi-objdump -d "../../database/${1}/samd20-xpro/${1}.elf" > out1
    arm-none-eabi-objdump -d "../../database/${2}/samd20-xpro/${2}.elf" > out2

    diff -a out1 out2 > diff_elf_samd20
    echo Lines: $(wc -l diff_elf_samd20)

    cp diff_elf_samd20 "samd20-xpro/elf_${1}__${2}"

    # samd21-xpro
    arm-none-eabi-objdump -d "../../database/${1}/samd20-xpro/${1}.elf" > out1
    arm-none-eabi-objdump -d "../../database/${2}/samd20-xpro/${2}.elf" > out2

    diff -a out1 out2 > diff_elf_samd21
    echo Lines: $(wc -l diff_elf_samd21)

    cp diff_elf_samd21 "samd21-xpro/elf_${1}__${2}"
fi 

if [ $command = map ] || [ $command = all ]; then
    # samd20-xpro
    out1="../../database/${1}/samd20-xpro/${1}.map"
    out2="../../database/${2}/samd20-xpro/${2}.map"

    diff -a $out1 $out2 > diff_map_samd20
    echo Lines: $(wc -l diff_map_samd20)

    cp diff_map_samd20 "samd20-xpro/map_${1}__${2}"

    # samd21-xpro
    out1="../../database/${1}/samd21-xpro/${1}.map"
    out2="../../database/${2}/samd21-xpro/${2}.map"

    diff -a $out1 $out2 > diff_map_samd21
    echo Lines: $(wc -l diff_map_samd21)

    cp diff_map_samd21 "samd21-xpro/map_${1}__${2}"
fi

rm out1 out2

rm diff_bin_samd20 diff_bin_samd21
rm diff_elf_samd20 diff_elf_samd21
rm diff_map_samd20 diff_map_samd21

echo Done!
