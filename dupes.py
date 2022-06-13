#!/usr/bin/env python3

"""Duplicate files checker"""

__version__ = "0.1.0"

import argparse
import filecmp
import math
from pathlib import Path
import pathlib
import os
import shutil
import sys
import time

class DupesError(Exception):
    """Fatal program errors"""

    def __init__(self, args):
        super().__init__(args)

class DupeFinder:
    """Object for finding duplicate files"""

    ACTION_LIST = "list"
    ACTION_MOVE = "move"
    ACTION_DELETE = "delete"

    def __init__(self, _args):
        self.source: Path = _args.source
        self.target: Path = _args.target
        self.args = _args

    def start(self):
        """Start process of finding duplicate files"""

        self.source_files: 'list[Path]' = []
        self.target_files: 'list[Path]' = []
        self.dupe_files: 'list[Path]' = []

        self.si, self.ti = (0, 0)
        self.eta_check = time.time()
        self.eta = "?"

        if self.args.action == DupeFinder.ACTION_MOVE:
            self.dupe_dir: Path = self.args.move
            try:
                self.dupe_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise DupesError(f"cannot create directory for duplicates in {self.dupe_dir}, {e.args[1].lower()}")

        self.check_source_paths(self.source, False)
        self.check_target_paths(self.target, False)

        for (self.si, source) in enumerate(self.source_files):
            self.ti = 0
            self.log(f"Comparing {str(source)}")
            for (self.ti, target) in enumerate(self.target_files):

                if not self.args.verbose:
                    print(self.get_progress(), end="\r", file=sys.stderr)

                self.calculate_eta()

                if not target.exists():
                    continue

                self.log(f"  with {str(target)}")

                if self.compare(source, target):
                    self.dupe_action(source, target)
                    if self.args.one:
                        break

        if self.args.action == DupeFinder.ACTION_LIST:
            for dupe_file in self.dupe_files:
                print(str(dupe_file))

    def log(self, msg):
        """Log current task to stdout"""

        if not self.args.verbose:
            return

        print(f"[{self.get_progress()}] {msg}")

    def calculate_eta(self):
        """Calculate ETA of finding all duplicates"""

        files_count = len(self.source_files) * len(self.target_files)
        current_file = (self.si * len(self.target_files) + self.ti + 1)

        eta_sec = int((time.time() - self.eta_check) * (files_count - current_file))

        eta_min = eta_sec // 60
        eta_sec = eta_sec % 60

        if eta_min > 99:
            eta_min = 99
            eta_sec = 99
        else:
            eta_min = eta_min if eta_min >= 10 else f"0{eta_min}"
            eta_sec = eta_sec if eta_sec >= 10 else f"0{eta_sec}"

        self.eta = f"{eta_min}:{eta_sec}"

        self.eta_check = time.time()

    def get_progress(self):
        """Calculate, format and return progress of current task"""

        files_count = len(self.source_files) * len(self.target_files)
        current_file = (self.si * len(self.target_files) + self.ti + 1)
        progress = math.floor(current_file / files_count * 10000) / 100

        return f"{progress:6.2f}%, ETA: {self.eta:5s} "

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
            self.log(e)

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
            self.log(e)

    def compare(self, file1: Path, file2: Path):
        """Compare two files"""

        if self.args.shallow:
            return True if file1.name == file2.name else False

        return filecmp.cmp(file1, file2, False)

    def dupe_action(self, source_file, dupe_file):
        """Perform user-defined action on duplicate files"""

        if self.args.action == DupeFinder.ACTION_LIST:
            self.dupe_files.append(dupe_file)
            self.log("    duplicate found")
            return

        if self.args.action == DupeFinder.ACTION_MOVE:

            if self.args.keep_tree:
                self.dupe_dir.joinpath(dupe_file.parent.relative_to(self.target)).mkdir(parents=True, exist_ok=True)

            new_path = self.find_new_path(dupe_file)

            try:
                shutil.move(dupe_file, new_path)
                self.log(f"    moved duplicate to {str(new_path)}")
            except PermissionError as e:
                self.log(f"    cannot move file {str(dupe_file)} to {str(new_path)}, {e.args[1].lower()}")

            return

        if self.args.action == DupeFinder.ACTION_DELETE:

            while True:
                if self.args.no_confirm:
                    break

                print(f"Delete {str(dupe_file)}? [Y/n/a/q] ", end="")

                ans = input().strip().lower()

                if len(ans) == 0:
                    ans = "y"

                if ans == "y":
                    break

                if ans == "n":
                    return

                if ans == "a":
                    self.args.no_confirm = True
                    break

                if ans == "q":
                    sys.exit(0)
                    return

            try:
                os.remove(dupe_file)
                self.log(f"    deleted duplicate {str(dupe_file)}")
            except PermissionError as e:
                self.log(f"    cannot delete file {str(dupe_file)}, {e.args[1].lower()}")

            return

    def find_new_path(self, file_path: Path, trial: int=0):
        """Recursively find new name for duplicate file if it already exists"""

        if trial == 0:
            new_filename = file_path.name
        else:
            new_filename = f"{file_path.stem}_{trial}{file_path.suffix}"

        if self.args.keep_tree:
            new_path = self.dupe_dir.joinpath(file_path.parent.relative_to(self.target), new_filename)
        else:
            new_path = self.dupe_dir.joinpath(new_filename)

        if new_path.exists():
            new_path = self.find_new_path(file_path, trial + 1)
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

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("source", type=Path, help="file or directory to be looked for")
    parser.add_argument("target", type=Path, help="file or directory to look for duplicates")
    parser.add_argument("-r", "-R", "--recursive", action="store_true", help="check source and target recursively")
    parser.add_argument("-s", "--shallow", action="store_true", help="compare only file names")
    parser.add_argument("-1", "--one", action="store_true", help="assume only one possible duplicate")
    parser.add_argument("-a", "--action", choices=[DupeFinder.ACTION_LIST, DupeFinder.ACTION_MOVE, DupeFinder.ACTION_DELETE], default=DupeFinder.ACTION_LIST, help="action to perform on duplicate files (default: list)")
    parser.add_argument("-v", "--verbose", action="store_true", help="output what is being done")

    move_group = parser.add_argument_group("MOVE action")
    move_group.add_argument("--move", metavar="duplicates_dir", type=Path, help="directory to move duplicate files (forces --action move)")
    move_group.add_argument("--keep-tree", action="store_true", help="keep the same folder structure for duplicates in duplicates_dir as in the target")

    delete_group = parser.add_argument_group("DELETE action")
    delete_group.add_argument("--no-confirm", action="store_true", help="don't ask for any confirmation")

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