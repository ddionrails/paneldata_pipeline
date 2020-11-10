""" Entrypoint and functions for cli to test relations between metadata files."""
import argparse
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """Set up arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-folder", help="Path to the input metadata files.", type=_full_path
    )
    parser.add_argument(
        "-r",
        "--relational-file",
        help="JSON file containing relational information between files",
        type=_full_path,
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def _full_path(path: str) -> Path:
    return Path(path).resolve()
