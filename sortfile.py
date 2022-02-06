"""Sort files into subdirectories by date."""
import argparse
import pathlib
import shutil

from datetime import datetime


VERBOSE = False


def info(*s):
    """Emit informational output in verbose mode."""
    if VERBOSE:
        print(*s)


def main(args):
    """Sort files into subdirectories by date."""
    print(args)

    global VERBOSE
    VERBOSE = args.verbose

    # This format string will be used to build directory tree based on date
    if args.groupby == "y":
        datestr = "%Y/"
    elif args.groupby == "ym":
        datestr = "%Y{}%m/".format(args.sep)
    elif args.groupby == "ymd":
        datestr = "%Y{}%m{}%d/".format(args.sep, args.sep)

    info(f"Format string: '{datestr}'")

    # Get source and destination paths
    src = pathlib.Path(args.source)
    dst = pathlib.Path(args.out)
    dst.mkdir(exist_ok=True, parents=False)

    info(
        f"Source directory: {src.resolve()}",
        f"Destination directory: {dst.resolve()}",
    )

    file_count = 0

    # Recursively grab all files under source directory
    files = src.glob("**/*")

    for srcfile in files:

        # Skip directories
        if not srcfile.is_file():
            continue

        # Sort copy of file into appropriate timestamped directory
        modified = datetime.fromtimestamp(srcfile.stat().st_mtime)
        slug = modified.strftime(datestr)
        dstfile = dst / slug / srcfile.name
        dstfile.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy2(srcfile, dstfile)  # copy2 preserves metadata
        info("Copied '{}' to '{}'".format(srcfile, dstfile))

        file_count += 1

    # Summarize this run
    print("------- Summary -------")
    print(f"Sorted {file_count} files to '{dst.resolve()}'.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Sort files into subdirectories by date"
    )
    parser.add_argument(
        "source", metavar="sourcedir", type=str, help="directory to sort"
    )
    parser.add_argument("--out", type=str, required=True, help="output directory")
    parser.add_argument(
        "--groupby",
        choices=["y", "ym", "ymd"],
        required=True,
        help="group by year, month, day, etc.",
    )
    parser.add_argument(
        "--sep", type=str, default="-", help="separator for directory names"
    )
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )

    args = parser.parse_args()

    main(args)
