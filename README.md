# dedup

Scripts for file and directory munging. 

### Requirements: ###

* Linux (the file mod date stuff will probably not work on a non-Linux OS)
* Python 3.6+

### Examples:

`dedup.py` is designed to merge all files from a set of source directories into a single flattened directory; if there are any duplicate filenames, the md5s are compared and a warning printed if they do not agree.

```
$ python dedup.py \
    directory1/ directory2/ directory3/ \
    --out combined_files/ \
    --verbose
```

`sortfile.py` was created to take a directory with files and copy them into into dated subdirectories according to the file modification timestamp (mtime).

```
$ python sortfile.py combined_files/ \
    --groupby ym \
    --out sorted_combined_files/ \
    --sep "" \
    --verbose
```

