
mkdir %3\samd20-xpro\deltagen_%1_%2\
mkdir %3\samd21-xpro\deltagen_%1_%2\

DeltaGenerator.exe -p "..\..\%3\%1\samd20-xpro\%1.bin" -n "..\..\%3\%2\samd20-xpro\%2.bin" --log > "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_%2.log" -o "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_%2"
DeltaGenerator.exe -p "..\..\%3\%1\samd21-xpro\%1.bin" -n "..\..\%3\%2\samd21-xpro\%2.bin" --log > "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_%2.log" -o "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_%2"
