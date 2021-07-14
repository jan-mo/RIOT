echo xxd/obj/both:
read command

if [[ $command = xxd ]]; then
    xxd $1 > out1
    xxd $2 > out2

    diff -a out1 out2 > diff_xxd

elif [[ $command = obj ]]; then
    arm-none-eabi-objdump -d $1 > out1
    arm-none-eabi-objdump -d $2 > out2

    diff -a out1 out2 > diff_obj

elif [[ $command = both ]]; then
    xxd $1 > out1
    xxd $2 > out2

    diff -a out1 out2 > diff_xxd

    arm-none-eabi-objdump -d $1 > out1
    arm-none-eabi-objdump -d $2 > out2

    diff -a out1 out2 > diff_obj

else
    echo Wrong command!
fi

rm out1 out2
