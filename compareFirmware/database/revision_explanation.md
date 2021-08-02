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
- ADC support
- power management control
- LED toggle

### rev_01
- enables LIS2DH12

### rev_02
- change from LIS2DH12 to LIS3DH

### rev_03
- GNRC_NET support

### rev_04
- change ADC line from 0 to 1
