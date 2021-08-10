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
USEMODULE += lis3dh

# gnrc_networking
GNRC_NETIF_NUMOF := 1

USEMODULE += gnrc_netdev_default
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6
USEMODULE += gnrc_icmpv6_error
USEMODULE += gnrc_udp
USEMODULE += gnrc_icmpv6_echo

USEMODULE += ps
USEMODULE += netstats_l2
USEMODULE += netstats_ipv6

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
