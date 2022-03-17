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


class Command:
    def __init_subclass__(cls, /, name: str = None):
        if not name:
            name = cls.__name__.lower().replace("_", "-")

        parameters = {}
        subcommands = {}

        annotations = get_type_hints(cls)
        cls_vars = vars(cls)
        attributes = {
            name: (annotations.get(name, None), cls_vars.get(name, None))
            for name in annotations.keys() | cls_vars.keys()
        }

        for attr_name, item in attributes.items():
            type_, _ = item

            # Save the type for subcommands
            if is_command(type_):
                subcommands[attr_name] = type_
            # Save the type for parameters
            elif is_parameters(type_):
                parameters[attr_name] = type_

        meta = CommandMeta(name, parameters, subcommands)
        setattr(cls, COMMANDMETA, meta)

    def __new__(cls, *args, **kwargs):
        namespace = {}
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
            namespace[param_name] = param_cls()

        namespace[COMMANDMETA] = CommandMeta(meta.name, parameters, subcommands)

        instance = type(meta.name, (object,), namespace, *args, **kwargs)

        return instance
