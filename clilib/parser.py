from dataclasses import dataclass
from typing import Any

from .parameters import Parameter, PARAMDEF, CHILDPARAM, is_parameters


class ParameterCollisionError(Exception):
    def __init__(self, collisions: list[str], message: str = None):
        self.collisions = collisions
        if not message:
            message = f"Multiple defitions for the parameter strings: {collisions}"
        super().__init__(message)


@dataclass(frozen=True)
class ParameterMapping:
    owner: Any
    name: str
    definition: Parameter

    def set(self, value: Any):
        setattr(self.owner, self.name, value)


def flatten_parameters(parameters: Any) -> dict[str, ParameterMapping]:
    if not is_parameters(parameters):
        raise AttributeError("Object not decorated with `parameters`")

    flattened_params = {}

    for name, param in getattr(parameters, PARAMDEF).items():
        for param_name in param.names:
            flattened_params[param_name] = ParameterMapping(owner=parameters, name=name, definition=param)

    for child_param_attr_name in getattr(parameters, CHILDPARAM).keys():
        child = getattr(parameters, child_param_attr_name)
        child_params = flatten_parameters(child)
        if collisions := child_params.keys() & flattened_params.keys():
            raise ParameterCollisionError(collisions=collisions)

        flattened_params.update(child_params)

    return flattened_params
