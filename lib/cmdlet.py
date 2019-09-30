import argparse
import sys
from typing import Callable, List, Dict, Any

ArgsType = Dict[str, Any]


class Cmdlet:
    def __init__(self, name: str, helpmsg: str, runner: Callable):
        self.name = name
        self.helpmsg = helpmsg
        self.runner = runner
        self.args: ArgsType = {}

    # Convenient way to call argparse.add_argument by chaining
    def add_arg(self, name: str, **params) -> "Cmdlet":
        self.args[name] = params
        return self

    def add_command(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.helpmsg)
        for name, params in self.args.items():
            parser.add_argument(name, **params)


class Commander:
    def __init__(self, cmdlets: List[Cmdlet]):
        self.cmdlets = cmdlets

    def run(self):
        main_parser = argparse.ArgumentParser("Board Vector")
        subparsers = main_parser.add_subparsers(help="sub command help")

        for cmd in self.cmdlets:
            cmd.add_command(subparsers)

        args = main_parser.parse_args()
        command = sys.argv[1]

        for cmd in self.cmdlets:
            if command == cmd.name:
                cmd.runner(args)
