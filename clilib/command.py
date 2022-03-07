from __future__ import annotations
from typing import Any, Type, get_type_hints

from .parameters import is_parameters


SUBCOMMAND = "_subcommands"
PARAMETERS = "_parameters"
CONFIG = "_commandconfig"


def is_command(obj: Any) -> bool:
    return hasattr(obj, SUBCOMMAND) and hasattr(obj, PARAMETERS)


def command_init(self, *args, **kwargs):
    """Command constructor. Instantiates the parameters and assigns them to the instance attributes."""

    for param_name, param_cls in getattr(self, PARAMETERS).items():
        setattr(self, param_name, param_cls())


def command(cls: Type = None, name: str = None):
    command_config = {"name": name}

    def wrap(cls):
        # Command methods
        setattr(cls, "__init__", command_init)

        # Configuration
        setattr(cls, CONFIG, command_config)

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

        setattr(cls, SUBCOMMAND, sub_commands)
        setattr(cls, PARAMETERS, parameters)

        return cls

    if cls is None:
        return wrap
    else:
        return wrap(cls)


def get_subcommands(obj: Any) -> dict[str, Type]:
    return getattr(obj, SUBCOMMAND)


def get_parameters(obj: Any) -> dict[str, Any]:
    return {name: getattr(obj, name) for name in getattr(obj, PARAMETERS).keys()}
