from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Type, cast, get_type_hints

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


class Parameters:
    def __init_subclass__(cls, /, name: str = None, **kwargs):
        if not name:
            name = cls.__name__.lower()

        # Future parameter definition
        options = {}
        arguments = {}
        child_parameters = {}

        # Collect all the attribute names, values, and types
        annotations = get_type_hints(cls)
        cls_vars = vars(cls)
        attributes = {
            name: (annotations.get(name, None), cls_vars.get(name, None))
            for name in annotations.keys() | cls_vars.keys()
        }

        for attr_name, item in attributes.items():
            type_, value = item

            # Copy the parameter definition to the _paramdef dictionary
            # Assign the default value to the attribute
            # If there's no type annotation, make the default a string
            if isinstance(value, Option) or isinstance(value, Flag):
                options[attr_name] = value
                annotations.setdefault(attr_name, Optional[str])
            elif isinstance(value, Argument):
                arguments[attr_name] = value
                annotations.setdefault(attr_name, str)
            # Save child parameter groups
            elif type_ and issubclass(type_, Parameters):
                child_parameters[attr_name] = type_

        meta = ParameterMeta(options, arguments, child_parameters, name=name)
        setattr(cls, PARAMMETA, meta)
        setattr(cls, "__annotations__", annotations)

    def __new__(cls, *args, **kwargs):
        namespace = dict(vars(cls))
        meta = get_param_meta(cls)

        options = {}
        arguments = {}
        param_children = {}
        for mro_cls in reversed(cls.__mro__):
            if not is_parameters(mro_cls):
                continue
            meta = get_param_meta(mro_cls)
            arguments.update(meta.argument_defs)
            options.update(meta.option_defs)
            param_children.update(meta.child_params)

        for name, value in {**arguments, **options}.items():
            if value.default:
                namespace[name] = value.default  # Set value from default
            else:
                namespace[name] = None

        # Instantiate child parameter groups
        for name, type_ in param_children.items():
            child = type_()
            namespace[name] = child

        namespace[PARAMMETA] = ParameterMeta(options, arguments, param_children, meta.name)
        instance = type(cls.__name__, (object,), namespace, *args, **kwargs)

        return cast(cls, instance)
