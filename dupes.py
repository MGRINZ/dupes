#!/usr/bin/env python3

"""Duplicate files checker"""

__version__ = "0.1.0"

import argparse
import filecmp
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

    ACTION_LIST = "list"

    def __init__(self, _args):
        self.source: Path = _args.source
        self.target: Path = _args.target
        self.args = _args

    def start(self):
        self.source_files: 'list[Path]' = []
        self.target_files: 'list[Path]' = []
        self.dupe_files: 'list[Path]' = []

        self.check_source_paths(self.source, False)
        self.check_target_paths(self.target, False)

        for source in self.source_files:
            print(f"Comparing {str(source)}")
            for target in self.target_files:

                if not target.exists():
                    break

                print(f"  with {str(target)}")

                if self.compare(source, target):
                    self.dupe_action(source, target)
                    if self.args.one:
                        break

        if self.args.action == DupeFinder.ACTION_LIST:
            for dupe_file in self.dupe_files:
                print(str(dupe_file))

    def check_source_paths(self, source: Path, recursive: bool=False):
        try:
            if source.is_dir():
                if recursive or source == self.source: # "or" for always checking provided directory
                    for path in source.iterdir():
                        self.check_source_paths(path, self.args.recursive)
            else:
                self.source_files.append(source)
        except PermissionError as e:
            print(e)

    def check_target_paths(self, target: Path, recursive: bool=False):
        try:
            if target.is_dir():
                if recursive or target == self.target: # "or" for always checking provided directory
                    for path in target.iterdir():
                        self.check_target_paths(path, self.args.recursive)
            else:
                self.target_files.append(target)
        except PermissionError as e:
            print(e)

    def compare(self, file1: Path, file2: Path):
        if self.args.shallow:
            return True if file1.name == file2.name else False

        return filecmp.cmp(file1, file2, False)

    def dupe_action(self, source_file, dupe_file):
        if self.args.action == DupeFinder.ACTION_LIST:
            self.dupe_files.append(dupe_file)
            print("    dupe found")

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
    parser.add_argument("-a", "--action", choices=[DupeFinder.ACTION_LIST], default=DupeFinder.ACTION_LIST, help="action to perform on duplicate files")

    return parser.parse_args()

if __name__ == "__main__":
    try:
        main()
    except DupesError as e:
        print(f"{sys.argv[0].split('/')[-1]}: error: {e}")
        sys.exit(1)