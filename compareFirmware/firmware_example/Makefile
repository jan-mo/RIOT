# name of your application
APPLICATION = firmware_example

# If no BOARD is found in the environment, use this default:
BOARD ?= samd21-xpro

# shell
USEMODULE += shell
USEMODULE += shell_commands

# sensors/devices
FEATURES_REQUIRED += periph_adc
FEATURES_REQUIRED += periph_usbdev
FEATURES_REQUIRED += periph_gpio_irq

# USB Ethernet and gnrc_networking
GNRC_NETIF_NUMOF := 1

USEMODULE += usbus_cdc_ecm
USEMODULE += auto_init_usbus
USEMODULE += gnrc_netdev_default
USEMODULE += auto_init_gnrc_netif
USEMODULE += gnrc_ipv6
USEMODULE += gnrc_icmpv6_error
USEMODULE += gnrc_udp
USEMODULE += gnrc_icmpv6_echo

USEMODULE += ps
USEMODULE += netstats_l2
USEMODULE += netstats_ipv6

USB_VID ?= 1234
USB_PID ?= 33ab
CFLAGS += -DUSB_CONFIG_VID=0x$(USB_VID) -DUSB_CONFIG_PID=0x$(USB_PID)


# This has to be the absolute path to the RIOT base directory:
RIOTBASE ?= $(CURDIR)/../..

# Comment this out to disable code in RIOT that does safety checking
# which is not needed in a production environment but helps in the
# development process:
DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1

include $(RIOTBASE)/Makefile.include
