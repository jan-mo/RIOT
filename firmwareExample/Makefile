# name of your application
APPLICATION = firmware_example

# If no BOARD is found in the environment, use this default:
BOARD ?= samd21-xpro

# shell
USEMODULE += shell
USEMODULE += shell_commands

# sensors/devices
FEATURES_REQUIRED += periph_adc
FEATURES_REQUIRED += periph_gpio_irq

# acceleration sensor
USEMODULE += lis2dh12_spi

# gnrc_networking
GNRC_NETIF_NUMOF := 1
USEMODULE += gnrc_netdev_default
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6
USEMODULE += gnrc_icmpv6_error
USEMODULE += gnrc_ipv6_router_default
USEMODULE += gnrc_udp
USEMODULE += gnrc_icmpv6_echo

USEMODULE += ps
USEMODULE += netstats_l2
USEMODULE += netstats_ipv6

# riotboot/suit
#USEMODULE += nanocoap_sock sock_util
USEMODULE += suit
BUILD_FILES += $(SLOT_RIOT_ELFS:%.elf=%.bin)

# WINC1500 WIFI
USEMODULE += atwinc15x0
# set the right SSID and PW for our WIFI
#USEMODULE += SET_SSID_AND_PW_OF_WIFI # reminder to set the SSID and PW in next line CFLAGS
CFLAGS += -DWIFI_SSID=\"***\" -DWIFI_PASS=\"***\"

# PCD8544
USEMODULE += pcd8544

# This has to be the absolute path to the RIOT base directory:
RIOTBASE ?= $(CURDIR)/..

# Comment this out to disable code in RIOT that does safety checking
# which is not needed in a production environment but helps in the
# development process:
DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1

include $(RIOTBASE)/Makefile.include
