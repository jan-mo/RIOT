
mkdir samd20-xpro\deltagen_%1_%2\
mkdir samd21-xpro\deltagen_%1_%2\

DeltaGenerator.exe -p "..\..\database\%1\samd20-xpro\%1.bin" -n "..\..\database\%2\samd20-xpro\%2.bin" --log > "samd20-xpro\deltagen_%1_%2\deltagen_%1_%2.log" -o "samd20-xpro\deltagen_%1_%2\deltagen_%1_%2"
DeltaGenerator.exe -p "..\..\database\%1\samd21-xpro\%1.bin" -n "..\..\database\%2\samd21-xpro\%2.bin" --log > "samd21-xpro\deltagen_%1_%2\deltagen_%1_%2.log" -o "samd21-xpro\deltagen_%1_%2\deltagen_%1_%2"
