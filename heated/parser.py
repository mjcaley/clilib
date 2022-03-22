from typing import Optional, Type
import sys

from .compiler import CompilerAction, CompilerArgument, CompilerCommand, CompilerOption, CompilerStore, CompilerStoreBool


class Parser:
    def __init__(self, compiler_command: CompilerCommand, args: list[str]):
        self.compiler_command = compiler_command
        self._args_iter = iter(args)
        self.current_arg = None

    def next_arg(self) -> str:
        try:
            self.current_arg = next(self._args_iter)
        except StopIteration:
            self.current_arg = None

    def parse_action(self, action: CompilerAction):
        if isinstance(action, CompilerStore):
            value = self.current_arg
            action.set(value)
            self.next_arg()
        elif isinstance(action, CompilerStoreBool):
            action.set()

    def parse_argument(self, argument: CompilerArgument):
        self.parse_action(argument.action)

    def parse_option(self, option: CompilerOption):
        if isinstance(option.child, CompilerAction):
            self.parse_action(option.child)
        elif isinstance(option.child, CompilerArgument):
            self.parse_argument(option.child)

    def parse_command(self):
        end_opts = False
        iter_compiler_arg = iter(self.compiler_command.arguments)
        next_command = None
        self.next_arg()

        while self.current_arg:
            if self.current_arg == "--":
                end_opts = True
                self.next_arg()

            if end_opts:
                for argument in iter_compiler_arg:
                    self.parse_argument(argument)
                break

            if subcommand := self.compiler_command.subcommands.get(self.current_arg):
                self.next_arg()
                next_command = subcommand
                break
            elif option := self.compiler_command.options.get(self.current_arg):
                self.next_arg()
                self.parse_option(option)
            else:
                argument = next(iter_compiler_arg)
                self.parse_argument(argument)

            continue

        last_args = [arg for arg in self._args_iter]
        if self.current_arg:
            remaining_args = [self.current_arg] + last_args
        else:
            remaining_args = last_args

        return next_command, remaining_args


    @classmethod
    def parse_args(cls, compiler_command: CompilerCommand, args: list[str] = None) -> tuple[Optional[Type], list[str]]:
        if args is None:
            args = sys.argv[1:]

        parser = cls(compiler_command, args)
        next_command, remaining_args = parser.parse_command()

        return next_command, remaining_args
