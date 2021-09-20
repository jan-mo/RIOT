# Revision explanation
The `firmware.diff` file in every reversion, consists of the diff between `rev_00` and the current revision.
The revision `rev_00` is the default version and every other firmware version can be restored.
The script `__restore_revision.sh` patches the `rev_00` default version.
You can build a new revision and automatically create the diff file, by running `make_copy.sh`.

## revision overview and functionality
All revisions are explained and the core functionality is listed

### rev_00
- default version
- shell commands
- ADC support (`PB00`)
- power management control
- LED toggle (`LED0`)

### rev_01
- enables LIS2DH12
- LIS2DH12 connected to `SPI(2)`

### rev_02
- change from LIS2DH12 to LIS3DH
- LIS3DH connected to `SPI(1)`

### rev_03
- GNRC_NET support

### rev_04
- change `ADC_LINE` from 0 to 1
- ADC connected to `PB01`

### rev_05
- enables PCD8544 display
- ADC and LIS values are displayed on screen

### rev_06
- threading for ADC and LIS periodic read

### rev_07
- modification in PCD8544 driver
- added functionality to write full line

### rev_08
- LIS support for LIS3DH and LIS2DH12
- can be defined by setting the specific `USEMODULE`

### rev_09
- updating RIOT OS to newer version
- update from 2021.04 to 2021.07

### rev_10
- modifying interrupt functionality of user button

### rev_11
- adding graphical view for ADC or LIS data