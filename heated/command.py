from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Type, Union, get_type_hints

from heated.context import Context

from .parameters import Parameters, is_parameters


COMMANDMETA = "_command_meta_"


@dataclass(frozen=True)
class CommandMeta:
    name: str
    parameters: dict[str, Type] = field(default_factory=dict)
    subcommands: dict[str, Type] = field(default_factory=dict)


class Command:
    def __init__(self, context: Context):
        self.context = context

    def invoke(self) -> None:
        pass

    def __init_subclass__(cls, /, name: str = None):
        if not name:
            name = cls.__name__.lower().replace("_", "-")

        parameters = {}
        subcommands = {}

        annotations = get_type_hints(cls)

        for attr_name, type_ in annotations.items():
            # Save the type for subcommands
            if is_command(type_):
                subcommands[attr_name] = type_
            # Save the type for parameters
            elif is_parameters(type_):
                parameters[attr_name] = type_

        meta = CommandMeta(name, parameters, subcommands)
        setattr(cls, COMMANDMETA, meta)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        meta = get_command_meta(cls)

        parameters = {}
        subcommands = {}
        for mro_cls in reversed(cls.__mro__):
            if not is_command(mro_cls):
                continue
            mro_meta = get_command_meta(mro_cls)
            parameters.update(mro_meta.parameters)
            subcommands.update(mro_meta.subcommands)

        for param_name, param_cls in meta.parameters.items():
            setattr(instance, param_name, param_cls())

        return instance


def is_command(obj: Any) -> bool:
    return hasattr(obj, COMMANDMETA)


def get_command_meta(command: Union[Command, Type]) -> CommandMeta:
    return getattr(command, COMMANDMETA)


def get_parameter_instances(command: Command) -> dict[str, Parameters]:
    meta = get_command_meta(command)

    return {attr_name: getattr(command, attr_name) for attr_name in meta.parameters}
