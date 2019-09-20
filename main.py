# The main interface for the program. Divides everything into sub
# commands for an easy to use iterface with a single entry point.

import argparse
import sys
import asset_manager as assets
from pathlib import Path


def add(args):
    mgr = assets.AssetManager()
    mgr.add(Path(args.photopath), assets.get_points(args))


def delete(args):
    mgr = assets.AssetManager()
    mgr.delete(args.n)


command_map = {"add": add, "delete": delete}

if __name__ == "__main__":
    main_parser = argparse.ArgumentParser("Board Vector")

    subparsers = main_parser.add_subparsers(help="sub command help")

    assets.add_add_parser(subparsers)
    assets.add_delete_parser(subparsers)

    args = main_parser.parse_args()

    command = sys.argv[1]

    if command not in command_map:
        raise ValueError

    command_map[command](args)
