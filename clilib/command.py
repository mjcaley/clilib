from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Type, get_type_hints

from .parameters import is_parameters


COMMANDMETA = "_command_meta_"


@dataclass(frozen=True)
class CommandMeta:
    name: str
    parameters: dict[str, Type]
    subcommands: dict[str, Type] = field(default_factory=dict)


def is_command(obj: Any) -> bool:
    return hasattr(obj, COMMANDMETA)


def get_command_meta(command: Any) -> CommandMeta:
    return getattr(command, COMMANDMETA)


def command_init(self):
    """Command constructor. Instantiates the parameters and assigns them to the instance attributes."""

    meta = get_command_meta(self)
    for param_name, param_cls in meta.parameters.items():
        setattr(self, param_name, param_cls())


def command(cls: Type = None, name: str = None):
    command_name = name or cls.__name__.lower().replace("_", "-")

    def wrap(cls):
        # Command methods
        setattr(cls, "__init__", command_init)

        # Mappings to types
        parameters = {}
        sub_commands = {}

        annotations = get_type_hints(cls)
        cls_vars = vars(cls)
        attributes = {
            name: (annotations.get(name, None), cls_vars.get(name, None))
            for name in annotations.keys() | cls_vars.keys()
        }

        for name, item in attributes.items():
            type_, _ = item

            # Save the type for subcommands
            if is_command(type_):
                sub_commands[name] = type_
                setattr(cls, name, None)
            # Save the type for parameters
            elif is_parameters(type_):
                parameters[name] = type_
                setattr(cls, name, None)

        meta = CommandMeta(command_name, parameters, sub_commands)
        setattr(cls, COMMANDMETA, meta)

        return cls

    if cls is None:
        return wrap
    else:
        return wrap(cls)
