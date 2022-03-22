from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Type, get_type_hints


PARAMMETA = "_param_meta_"


@dataclass
class ParameterMeta:
    definitions: dict[str, Parameter] = field(default_factory=dict)
    child_parameters: dict[str, Type] = field(default_factory=dict)
    name: Optional[str] = None


def is_parameters(obj: Any) -> bool:
    return hasattr(obj, PARAMMETA)


def get_param_meta(parameters: Any) -> ParameterMeta:
    return getattr(parameters, PARAMMETA)


# region Parameter definitions


class Parameter:
    def __init__(self, *names: str, default=None, help: str = ""):
        self.names = set(names)
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
        parameters = {}
        child_parameters = {}

        # Collect all the attribute names, values, and types
        annotations = get_type_hints(cls)
        cls_vars = vars(cls)

        for attr_name, definition in cls_vars.items():
            # Copy the parameter definition to the _paramdef dictionary
            # Assign the default value to the attribute
            # If there's no type annotation, make the default a string
            if isinstance(definition, Option) or isinstance(definition, Flag):
                parameters[attr_name] = definition
                annotations.setdefault(attr_name, Optional[str])
            elif isinstance(definition, Argument):
                parameters[attr_name] = definition
                annotations.setdefault(attr_name, str)

        # Save child parameter groups
        for attr_name, type_ in annotations.items():
            if type_ and issubclass(type_, Parameters):
                child_parameters[attr_name] = type_

        meta = ParameterMeta(
            definitions=parameters, child_parameters=child_parameters, name=name
        )
        setattr(cls, PARAMMETA, meta)
        setattr(cls, "__annotations__", annotations)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        meta = get_param_meta(cls)

        definitions = {}
        param_children = {}
        for mro_cls in reversed(cls.__mro__):
            if not is_parameters(mro_cls):
                continue
            meta = get_param_meta(mro_cls)
            definitions.update(meta.definitions)
            param_children.update(meta.child_parameters)

        for name, value in definitions.items():
            if value.default:
                setattr(instance, name, value.default)  # Set value from default
            else:
                setattr(instance, name, None)

        # Instantiate child parameter groups
        for name, type_ in param_children.items():
            child = type_()
            setattr(instance, name, child)

        return instance


@dataclass(frozen=True)
class FlatParameter:
    owner: Any
    member_name: str
    annotation: Type
    parameter: Parameter


def flatten_parameters(*parameters: Parameter) -> tuple[FlatParameter]:
    param_result = []

    for parameter in parameters:
        if not is_parameters(parameter):
            continue

        meta = get_param_meta(parameter)
        annotations = get_type_hints(parameter)
        for attr_name, definition in meta.definitions.items():
            param_result.append(
                FlatParameter(
                    owner=parameter,
                    member_name=attr_name,
                    annotation=annotations[attr_name],
                    parameter=definition,
                )
            )

        child_attr = [
            getattr(parameter, attr_name) for attr_name in meta.child_parameters
        ]
        child_params = flatten_parameters(*child_attr)
        param_result.extend(child_params)

    return tuple(param_result)
