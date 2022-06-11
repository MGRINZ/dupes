#!/usr/bin/env python3

"""Duplicate files checker"""

__version__ = "0.1.0"

import argparse
from pathlib import Path
import pathlib
import os
import sys

class DupesError(Exception):
    """Fatal program errors"""

    def __init__(self, args):
        super().__init__(args)

class DupeFinder:
    """Object for finding duplicate files"""

    def __init__(self, _args):
        self.source: Path = _args.source
        self.target: Path = _args.target
        self.args = _args

    def start(self):
        pass

def main():
    args = parse_args()

    if not args.source.exists():
        raise DupesError("source file or directory doesn't exist")
    
    if not args.target.exists():
        raise DupesError("target file or directory doesn't exist")

    df = DupeFinder(args)
    df.start()

def parse_args():
    parser = argparse.ArgumentParser(description="Duplicate files checker")

    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("source", type=Path, help="file or directory to be looked for")
    parser.add_argument("target", type=Path, help="file or directory to look for duplicates")
    parser.add_argument("-r", "-R", "--recursive", action="store_true", help="check target and source recursively")
    parser.add_argument("-s", "--shallow", action="store_true", help="compare only file names")
    parser.add_argument("-1", "--one", action="store_true", help="assume only one possible duplicate")

    return parser.parse_args()

if __name__ == "__main__":
    try:
        main()
    except DupesError as e:
        print(f"{sys.argv[0].split('/')[-1]}: error: {e}")
        sys.exit(1)