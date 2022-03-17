from typing import Optional, Type
import sys

from .compiler import ParameterMapping


class Parser:
    def __init__(
        self,
        options: dict[str, ParameterMapping],
        arguments: list[ParameterMapping],
        subcommands: dict[str, Type],
    ):
        self.options = options
        self.arguments = arguments
        self.subcommands = subcommands

    def parse_args(self, args: list[str] = None) -> Optional[Type]:
        if args is None:
            args = sys.argv[1:]

        next_command: Optional[Type] = None
        arg_iter = iter(self.arguments.values())

        end_opts = False
        while len(args) > 0:
            current = args.pop(0)

            if not end_opts:
                if current == "--":
                    end_opts = True
                    continue

                if command_found := self.subcommands.get(current):
                    next_command = command_found
                    break

                if option := self.options.get(current):
                    value = args.pop(0)  # TODO: The argument may not take a value
                    option.set(value)
                    continue
                    # TODO: see if there's other arguments after too

            current_arg = next(arg_iter)
            current_arg.set(current)

        return next_command, [arg for arg in arg_iter]
