# database

- scripts for creating the database can be found in `scripts/`
- the output of scripts are stored in `output/`
- the revisions are stored belonging folder `rev_xx`
- `riotboot` contains the revision with activated riotboot and slots

## scipts

- `saving_database_info.sh` will save all information on database
- `make_copy.sh` builds and compiles the given revision (stored in `database`)
- `creat_slots.sh` will patch the revisions (stores slot0 and slot1 in `riotboot`)
