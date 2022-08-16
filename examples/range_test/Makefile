# name of your application
APPLICATION = range_test

# If no BOARD is found in the environment, use this default:
BOARD ?= lbc_at-v12

# This has to be the absolute path to the RIOT base directory:
RIOTBASE ?= $(CURDIR)/../..

# use the default network interface for the board
USEMODULE += netdev_default
USEMODULE += auto_init_gnrc_netif

USEMODULE += gnrc_ipv6_default
USEMODULE += gnrc_udp

USEMODULE += gnrc_icmpv6_echo

# USEMODULE += periph_uart_nonblocking

USEMODULE += shell
USEMODULE += shell_commands
USEMODULE += ps
USEMODULE += xtimer

USEMODULE += ztimer_no_periph_rtt

USEMODULE += periph_rtt

# Comment this out to disable code in RIOT that does safety checking
# which is not needed in a production environment but helps in the
# development process
DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1

# CFLAGS += -DIEEE802154_DEFAULT_PANID=$(DEFAULT_PAN_ID)

# comment out for 2.4 GHz radio usage
DISABLE_MODULE += at86rf215_24ghz
CFLAGS += -DCONFIG_AT86RF215_DEFAULT_TXPOWER=3

include $(RIOTBASE)/Makefile.include

# Set a custom channel if needed
include $(RIOTMAKE)/default-radio-settings.inc.mk
