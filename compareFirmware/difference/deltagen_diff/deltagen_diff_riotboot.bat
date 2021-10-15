
mkdir %3\samd20-xpro\deltagen_%1_%2\
mkdir %3\samd21-xpro\deltagen_%1_%2\

DeltaGenerator.exe -p "..\..\%3\%1\samd20-xpro\%1_slot0.bin" -n "..\..\%3\%2\samd20-xpro\%2_slot0.bin" --log > "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot0.log" -o "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot0"
DeltaGenerator.exe -p "..\..\%3\%1\samd20-xpro\%1_slot0.bin" -n "..\..\%3\%2\samd20-xpro\%2_slot1.bin" --log > "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot1.log" -o "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot1"
DeltaGenerator.exe -p "..\..\%3\%1\samd20-xpro\%1_slot1.bin" -n "..\..\%3\%2\samd20-xpro\%2_slot0.bin" --log > "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot0.log" -o "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot0"
DeltaGenerator.exe -p "..\..\%3\%1\samd20-xpro\%1_slot1.bin" -n "..\..\%3\%2\samd20-xpro\%2_slot1.bin" --log > "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot1.log" -o "%3\samd20-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot1"

DeltaGenerator.exe -p "..\..\%3\%1\samd21-xpro\%1_slot0.bin" -n "..\..\%3\%2\samd21-xpro\%2_slot0.bin" --log > "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot0.log" -o "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot0"
DeltaGenerator.exe -p "..\..\%3\%1\samd21-xpro\%1_slot0.bin" -n "..\..\%3\%2\samd21-xpro\%2_slot1.bin" --log > "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot1.log" -o "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot0_%2_slot1"
DeltaGenerator.exe -p "..\..\%3\%1\samd21-xpro\%1_slot1.bin" -n "..\..\%3\%2\samd21-xpro\%2_slot0.bin" --log > "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot0.log" -o "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot0"
DeltaGenerator.exe -p "..\..\%3\%1\samd21-xpro\%1_slot1.bin" -n "..\..\%3\%2\samd21-xpro\%2_slot1.bin" --log > "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot1.log" -o "%3\samd21-xpro\deltagen_%1_%2\deltagen_%1_slot1_%2_slot1"
