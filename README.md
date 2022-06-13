# Dupes

Dupes is a simple command line program for searching for duplicate files. It takes two positional arguments `source` and `target` as single file or directory and looks for `source` files in `target`. It is possible to specify an action to be performed on duplicated files in `target`: LIST them to standard output (default), MOVE them to another folder or DELETE them.

## Usage

### Command line arguments
```
$ dupes.py --help
usage: dupes.py [-a {list,move,delete}] [-1] [-r] [-s] [-v] [--version] [-h] [--move duplicates_dir] [--keep-tree] [--no-confirm] source target

Duplicate files checker

positional arguments:
  source                file or directory to be looked for
  target                file or directory to look for duplicates

options:
  -a {list,move,delete}, --action {list,move,delete}
                        action to perform on duplicate files (default: list)
  -1, --one             assume only one possible duplicate
  -r, -R, --recursive   check source and target recursively
  -s, --shallow         compare only file names
  -v, --verbose         output what is being done
  --version             show program's version number and exit
  -h, --help            show this help message and exit

MOVE action:
  --move duplicates_dir
                        directory to move duplicate files (forces --action move)
  --keep-tree           keep the same folder structure for duplicates in duplicates_dir as in the target

DELETE action:
  --no-confirm          don't ask for any confirmation
```

### List duplicate files

```
$ dupes.py source_dir target_dir
```

or set action LIST explicitly

```
$ dupes.py -a list source_dir target_dir
```

### Move duplicate files

With explicit MOVE action

```
$ dupes.py -a move --move duplicates_dir source_dir target_dir
```

or just

```
$ dupes.py --move duplicates_dir source_dir target_dir
```

Also you can keep `target_dir` folder tree in `duplicates_dir`

```
$ dupes.py --move duplicates_dir --keep-tree source_dir target_dir
```

### Delete duplicate files

Delete files (requires confirmation)

```
$ dupes.py -a delete source_dir target_dir
```

Delete files without asking

```
$ dupes.py -a delete --no-confirm source_dir target_dir
```

### Alter searching

Search recursively both `source` and `target`

```
$ dupes.py -r source_dir target_dir
```

Assume `target` may contain only one duplicate file of each `source` file

```
$ dupes.py -1 source_dir target_dir
```

Perform shallow searching that is compare only file names

```
$ dupes.py -s source_dir target_dir
```

All arguments above can be mixed

```
$ dupes.py -1rs source_dir target_dir
```