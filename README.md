# vndb_fetcher
Wrapper scripts for VNDB API

# Requirements

We recommend you to have the following components.

* Python3 (3.6.5 or above)
* Wget

# Usage

## Fetch the entire table

`client.py` fetches the table from VNDB using `get` command described in
[Public Database API](https://vndb.org/d11)
```
python3 client.py {type} {flag}
```
`type` argument is a subcommand of `get`, such as vn, release and so on.
`flag` argument limits the scope of member corresponding to `Flag` entry
shown in the scheme.
`flag` is optional and set as "basic" if not given.

For example, the command below fetches basic information of all visual novels
registered in VNDB.
```
python3 client.py vn
```
The result is saved as JSON file `data/vn_basic.json`.

When `type` was set as `dbstats`, `client.py` gives the result of `dbstats`
command as JSON file `data/dbstats.json`.
```
python3 client.py dbstats
```

## Download dumps

`dump.sh` simply downloads remaining database dumps to the `data` directory
via URLs listed in [Database Dumps](https://vndb.org/d14):
```
./dump.sh
```

# License

MIT License (see `LICENSE` file).
