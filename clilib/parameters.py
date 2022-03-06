from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Type, get_type_hints


# region Parameter definitions


class Parameter:
    def __init__(self, *names: str, default=None, help: str = ""):
        self.names = names
        self.default = default
        self.help = help


class Option(Parameter):
    def __init__(self, *names: str, default=None, help: str = ""):
        super().__init__(*names, default=default, help=help)


class Argument(Parameter):
    def __init__(self, *names: str, default=None, help: str = ""):
        super().__init__(*names, default=default, help=help)


class Flag(Parameter):
    def __init__(self, *names: str, default: bool = False, help: str = ""):
        super().__init__(*names, default=default, help=help)


# endregion


PARAMDEF = "_paramdef"


def param_init(self, *args, **kwargs):
    for name, value in getattr(self, PARAMDEF).items():
        if name in kwargs:
            setattr(self, name, kwargs[name])  # Set value from constructor
        elif value.default is not None:
            setattr(self, name, value.default)  # Set value from default


def parameters(cls: Type) -> Type:
    # Setup class methods
    setattr(cls, "__init__", param_init)

    # Future parameter definition
    parameters = {}

    # Collect all the attribute names, values, and types
    annotations = get_type_hints(cls)
    cls_vars = vars(cls)
    attributes = {
        name: (annotations.get(name, None), cls_vars.get(name, None))
        for name in annotations.keys() | cls_vars.keys()
    }

    for name, item in attributes.items():
        type_, value = item

        # Copy the parameter definition to the __paramdef__ dictionary
        # Assign the default value to the attribute
        # If there's no type annotation, make the default a string
        if isinstance(value, Parameter):
            parameters[name] = value
            setattr(cls, name, None)
            annotations.setdefault(name, str)

        # Instantiate child parameters
        elif hasattr(type_, PARAMDEF):
            setattr(cls, name, type_())

    setattr(cls, PARAMDEF, parameters)
    setattr(cls, "__annotations__", annotations)

    return cls


def is_parameters(obj: Any) -> bool:
    return hasattr(obj, PARAMDEF)
