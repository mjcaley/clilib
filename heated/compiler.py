from dataclasses import dataclass
from typing import Any, Type, Union

from .command import Command, get_command_meta, get_parameter_instances
from .parameters import (
    Argument,
    Flag,
    FlatParameter,
    Option,
    flatten_parameters,
)


class ParameterCollisionError(Exception):
    def __init__(self, collisions: set[str], message: str = None):
        self.collisions = collisions
        if not message:
            message = f"Multiple defitions for the parameter strings: {collisions}"
        super().__init__(message)


class CompilerAction:
    def set(self, value: Any):
        raise NotImplementedError


@dataclass
class CompilerStore(CompilerAction):
    type_: Type
    owner: Any
    member_name: str

    def set(self, value: Any):
        setattr(self.owner, self.member_name, self.type_(value))


@dataclass
class CompilerStoreBool(CompilerAction):
    owner: Any
    member_name: str
    value: bool = True

    def set(self):
        setattr(self.owner, self.member_name, self.value)


@dataclass
class CompilerArgument:
    action: CompilerAction


@dataclass
class CompilerOption:
    child: Union[CompilerAction, CompilerArgument]


@dataclass
class CompilerCommand:
    options: dict[str, CompilerOption]
    arguments: list[CompilerArgument]
    subcommands: dict[str, Command]


def compile_parameters(
    definitions: tuple[FlatParameter],
) -> tuple[list[CompilerArgument], dict[str, CompilerOption]]:
    seen_names = set()

    arguments = []
    options = {}

    for definition in definitions:
        if collision := seen_names & set(definition.parameter.names):
            raise ParameterCollisionError(collision)
        seen_names.update(definition.parameter.names)

        if isinstance(definition.parameter, Argument):
            action = CompilerStore(
                definition.annotation, definition.owner, definition.member_name
            )
            argument = CompilerArgument(action=action)
            arguments.append(argument)
        elif isinstance(definition.parameter, Option):
            action = CompilerStore(
                definition.annotation, definition.owner, definition.member_name
            )
            option = CompilerOption(child=action)
            for name in definition.parameter.names:
                options[name] = option
        elif isinstance(definition.parameter, Flag):
            action = CompilerStoreBool(
                definition.owner,
                definition.member_name,
                not definition.parameter.default,
            )
            option = CompilerOption(action)
            for name in definition.parameter.names:
                options[name] = option

    return arguments, options


def compile_command(command: Command) -> CompilerCommand:
    command_meta = get_command_meta(command)
    subcommands = {
        get_command_meta(subcommand).name: subcommand
        for subcommand in command_meta.subcommands.values()
    }

    parameter_instances = get_parameter_instances(command).values()
    flattened_params = flatten_parameters(*parameter_instances)
    arguments, options = compile_parameters(flattened_params)

    return CompilerCommand(options=options, arguments=arguments, subcommands=subcommands)
