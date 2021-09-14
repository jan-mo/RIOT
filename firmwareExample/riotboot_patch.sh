echo "FEATURES_PROVIDED += riotboot" >> ../boards/samd20-xpro/Makefile.features
echo "FEATURES_PROVIDED += riotboot" >> ../boards/samd21-xpro/Makefile.features
echo "USEMODULE += suit" > ../firmwareExample/tmp
echo "BUILD_FILES += \$(SLOT_RIOT_ELFS:%.elf=%.bin)" >> ../firmwareExample/tmp
cat ../firmwareExample/Makefile >> ../firmwareExample/tmp
cat ../firmwareExample/tmp > ../firmwareExample/Makefile
rm ../firmwareExample/tmp
