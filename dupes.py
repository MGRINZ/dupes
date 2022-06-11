#!/usr/bin/env python3

"""Duplicate files checker"""

__version__ = "0.1.0"

import argparse
import filecmp
from pathlib import Path
import pathlib
import os
import shutil
import sys

class DupesError(Exception):
    """Fatal program errors"""

    def __init__(self, args):
        super().__init__(args)

class DupeFinder:
    """Object for finding duplicate files"""

    ACTION_LIST = "list"
    ACTION_MOVE = "move"

    def __init__(self, _args):
        self.source: Path = _args.source
        self.target: Path = _args.target
        self.args = _args

    def start(self):
        """Start process of finding duplicate files"""

        self.source_files: 'list[Path]' = []
        self.target_files: 'list[Path]' = []
        self.dupe_files: 'list[Path]' = []

        if self.args.action == DupeFinder.ACTION_MOVE:
            self.dupe_dir: Path = self.args.move
            try:
                self.dupe_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise DupesError(f"cannot create directory for duplicates in {self.dupe_dir}, {e.args[1].lower()}")

        self.check_source_paths(self.source, False)
        self.check_target_paths(self.target, False)

        for source in self.source_files:
            print(f"Comparing {str(source)}")
            for target in self.target_files:

                if not target.exists():
                    continue

                print(f"  with {str(target)}")

                if self.compare(source, target):
                    self.dupe_action(source, target)
                    if self.args.one:
                        break

        if self.args.action == DupeFinder.ACTION_LIST:
            for dupe_file in self.dupe_files:
                print(str(dupe_file))

    def check_source_paths(self, source: Path, recursive: bool=False):
        """Generate list of source files"""

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
        """Generate list of target files"""

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
        """Compare two files"""

        if self.args.shallow:
            return True if file1.name == file2.name else False

        return filecmp.cmp(file1, file2, False)

    def dupe_action(self, source_file, dupe_file):
        """Perform user-defined action on duplicate files"""

        if self.args.action == DupeFinder.ACTION_LIST:
            self.dupe_files.append(dupe_file)
            print("    duplicate found")
        if self.args.action == DupeFinder.ACTION_MOVE:
            new_path = self.find_new_path(dupe_file.name)

            try:
                shutil.move(dupe_file, new_path)
                print(f"    moved duplicate to {str(new_path)}")
            except PermissionError as e:
                print(f"    cannot move file {str(dupe_file)} to {str(new_path)}, {e.args[1].lower()}")

    def find_new_path(self, filename: str, trial: int=0):
        """Recursively find new name for duplicate file if it already exists"""

        if trial == 0:
            new_filename = filename
        else:
            file_path = Path(filename)
            new_filename = f"{file_path.stem}_{trial}{file_path.suffix}"

        new_path = self.dupe_dir.joinpath(new_filename)

        if new_path.exists():
            new_path = self.find_new_path(filename, trial + 1)
        return new_path

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
    parser.add_argument("-a", "--action", choices=[DupeFinder.ACTION_LIST, DupeFinder.ACTION_MOVE], default=DupeFinder.ACTION_LIST, help="action to perform on duplicate files")
    parser.add_argument("--move", metavar="duplicates_dir", type=Path, help="directory to move duplicate files (forces --action move)")

    args = parser.parse_args()

    if args.action == DupeFinder.ACTION_MOVE and args.move is None:
        parser.error("you must specify directory for duplicates with --move duplicates_dir")

    if args.move is not None:
        args.action = DupeFinder.ACTION_MOVE

    return args

if __name__ == "__main__":
    try:
        main()
    except DupesError as e:
        print(f"{sys.argv[0].split('/')[-1]}: error: {e}")
        sys.exit(1)