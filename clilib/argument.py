from types import new_class
from typing import Any, Callable


class Argument:
    """User-defined arguments."""

    def __init__(self, *arguments, type_: Callable = str, default: Any = None):
        self.arguments = arguments
        self.type_ = type_
        self.default = default


class LongOption:
    def __init__(self, argument, type_: Callable = str, default: Any = None):
        self.argument = argument
        self.type_ = type_
        self.default = default


class ShortOption:
    def __init__(self, argument, type_: Callable = str, default: Any = None):
        self.argument = argument
        self.type_ = type_
        self.default = default


def argument_to_internal(argument: Argument) -> dict[str, Any]:
    internal_args = {}
    for name in argument.arguments:
        if name.startswith("--"):
            internal_name = name.lstrip("-")
            internal_args[internal_name] = LongOption(internal_name, argument.type_, argument.default)
        elif name.startswith("-"):
            internal_name = name.lstrip("-")
            internal_args[internal_name] = ShortOption(internal_name, argument.type_, argument.default)
        else:
            ...
            # TODO: Argument object

    return internal_args


def _assign_arg_init(cls, keys):
    def __init__(self, **kwargs):
        for key in keys:
            setattr(self, f"_{key}", None)
        for key, value in kwargs.items():
            setattr(self, f"_{key}", value)

    setattr(cls, "__init__", __init__)


def _make_getter(key):
    def getter(self):
        return getattr(self, f"_{key}")

    return getter


def _make_setter(key):
    def setter(self, value):
        setattr(self, f"_{key}", value)

    return setter


def _make_properties(keys, type=None):
    return {key: property(fget=_make_getter(key), fset=_make_setter(key)) for key in keys}


class ArgumentMetaClass(type):
    def __new__(mcls, name, bases, namespace: dict[str, Any]):
        print(f"attributes in {name}")

        arg_fields = {}
        new_namespace = {"_arg_fields": {}}
        arg_names = set()
        for key, value in namespace.items():
            if isinstance(value, Argument):
                arg_names.add(key)
                print(f"Adding {key}: {value} as argument")
                internal_args = argument_to_internal(value)
                arg_fields.update(internal_args)
                properties = _make_properties(internal_args.keys())
                new_namespace.update(properties)
                new_namespace[f"_{key}"] = None  # Initialize the backing field
                # Replace type annotation with option type
            else:
                new_namespace[key] = value
        new_namespace["_arg_fields"].update(arg_fields)

        cls = super().__new__(mcls, name, bases, new_namespace)

        return cls


class Arguments(metaclass=ArgumentMetaClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, f"_{key}", value)

    def _parse(self, args: list[str]):
        pass
