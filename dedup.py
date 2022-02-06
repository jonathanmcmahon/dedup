"""Deduplicate files from multiple directories."""
import argparse
import hashlib
import pathlib
import shutil


VERBOSE = False


def info(*s):
    """Emit informational output in verbose mode."""
    if VERBOSE:
        print(*s)


def file_as_bytes(file):
    """Read and return a file object as bytes."""
    with file:
        return file.read()


def main(args):
    """Deduplicate files from multiple directories."""
    global VERBOSE
    VERBOSE = args.verbose

    # Print arguments
    info("Arguments:")
    for k, v in args._get_kwargs():
        if v is not None:
            info(
                "\t{}\t{}".format(
                    f"{k}:".ljust(10, " "),
                    v,
                )
            )

    # File extension for filtering
    dot_ext = f".{args.ext}" if args.ext else ""

    # Collect all source directories
    srcpaths = []
    info("Combining files from directories:")
    for src in args.sources:
        src = pathlib.Path(src)
        info(f"\t '{src.resolve()}'")
        srcpaths.append(src)

    skip_count = 0
    conflict_count = 0

    conflicts = []
    files = {}

    # Loop over source directories
    for src in srcpaths:
        # Grab all files, filtering on file extension if given
        flist = src.glob(f"**/*{dot_ext}")

        # Process each filesystem object found
        for path in flist:

            # Skip directories
            if not path.is_file():
                continue

            fname = path.name

            metadata = {
                "file": path,
                "filename": fname,
            }

            # Check for duplicate filenames
            if fname not in files:
                # For new files, add metadata to list of files
                files[fname] = metadata
            else:  # if filename has already been seen, we must deconflict

                # We only compare checksums if we encounter a situation
                # where there are multiple files with the same file name
                metadata["md5"] = hashlib.sha256(
                    file_as_bytes(open(path, "rb"))
                ).digest()

                files[fname]["md5"] = hashlib.sha256(
                    file_as_bytes(open(files[fname]["file"], "rb"))
                ).digest()

                # If checksums do not match, we will track these files
                # and print a warning
                if files[fname]["md5"] != metadata["md5"]:
                    conflicts.append((files[fname], metadata))
                    print(
                        "[WARNING] conflict: md5 mismatch for '{}' and '{}'; keeping first and skipping second".format(
                            files[fname]["file"], metadata["file"]
                        )
                    )
                    conflict_count += 1

                # If checksums do match, we are dealing with two copies of
                # the same file and we just ignore the second copy
                else:
                    info(
                        "Skipping file '{}' (duplicate of '{}')".format(
                            path,
                            files[fname]["file"],
                        )
                    )
                skip_count += 1

    # Create output directory if it doesn't exist
    out = pathlib.Path(args.out)
    out.mkdir(parents=False, exist_ok=True)

    # Copy files to output directory
    i = 0
    for _, meta in files.items():
        i += 1
        srcfile = meta["file"]
        # Copy to output dir
        dstfile = out / srcfile.name
        # Try to preserve metadata by using copy2
        shutil.copy2(srcfile, dstfile)
        info(
            "Copied '{}' to '{}' (file {} / {})".format(srcfile, dstfile, i, len(files))
        )

    # Summarize this run
    print("------- Summary -------")
    print(
        "Found {} unique files in {} directories; skipped {} duplicates.".format(
            len(files),
            len(srcpaths),
            skip_count,
        )
    )
    print(
        "Out of {} duplicate file names, there were {} md5 mismatches.".format(
            skip_count,
            conflict_count,
        )
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Deduplicate files from multiple directories"
    )
    parser.add_argument(
        "sources",
        type=str,
        nargs="+",
        help="source directory or directories for deduplication",
    )
    parser.add_argument("--out", type=str, required=True, help="output directory")
    parser.add_argument("--ext", type=str, help="only merge files with this extension")
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )
    # TODO: Add option to skip checksumming
    # parser.add_argument("--skipchecksum", help="skip checksum verification (faster)",
    #                action="store_true")

    args = parser.parse_args()

    main(args)
