from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional, Type, get_type_hints


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


PARAMMETA = "_param_meta_"


@dataclass
class ParameterMeta:
    option_defs: dict[str, Parameter]
    argument_defs: dict[str, Parameter]
    child_params: dict[str, Type]
    name: Optional[str] = None


def is_parameters(obj: Any) -> bool:
    return hasattr(obj, PARAMMETA)


def get_param_meta(parameters: Any) -> ParameterMeta:
    return getattr(parameters, PARAMMETA)


def param_init(self, *_, **kwargs):
    meta = get_param_meta(self)

    param_defs = {**meta.argument_defs, **meta.option_defs}

    for name, value in param_defs.items():
        if name in kwargs:
            setattr(self, name, kwargs[name])  # Set value from constructor
        elif value.default is not None:
            setattr(self, name, value.default)  # Set value from default

    # Instantiate child parameter groups
    for name, type_ in meta.child_params.items():
        child = type_()
        setattr(self, name, child)


def parameters(cls: Type) -> Type:
    # Setup class methods
    setattr(cls, "__init__", param_init)

    # Future parameter definition
    options = {}
    arguments = {}
    child_parameters = {}

    # Collect all the attribute names, values, and types
    # TODO: Traverse MRO to get inherited members
    annotations = get_type_hints(cls)
    cls_vars = vars(cls)
    attributes = {
        name: (annotations.get(name, None), cls_vars.get(name, None))
        for name in annotations.keys() | cls_vars.keys()
    }

    for name, item in attributes.items():
        type_, value = item

        # Copy the parameter definition to the _paramdef dictionary
        # Assign the default value to the attribute
        # If there's no type annotation, make the default a string
        if isinstance(value, Option) or isinstance(value, Flag):
            options[name] = value
            setattr(cls, name, None)
            annotations.setdefault(name, Optional[str])
        elif isinstance(value, Argument):
            arguments[name] = value
            setattr(cls, name, None)
            annotations.setdefault(name, str)

        # Save child parameter groups
        elif is_parameters(type_):
            setattr(cls, name, None)
            child_parameters[name] = type_

    meta = ParameterMeta(options, arguments, child_parameters, name=None)
    setattr(cls, PARAMMETA, meta)
    setattr(cls, "__annotations__", annotations)

    return cls
