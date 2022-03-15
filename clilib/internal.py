from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Type, get_type_hints

from .parameter import Parameter, Argument, Option


@dataclass
class UserParameterDefinition:
    name: str
    type_: Type
    value: Any


class InternalParameters:
    @classmethod
    def from_parameter(cls, param: Parameter) -> InternalParameters:
        param_types = get_type_hints(param)
        params = [
            UserParameterDefinition(name, param_types[name], value)
            for name, value in vars(param).items()
            if isinstance(value, Parameter)
        ]

        return cls(params)

    def __init__(self, parameters: list[UserParameterDefinition]):
        self.parameters = parameters

    def identifiers(self) -> set[str]:
        return self.parameters.keys()

    def short_params(self) -> set[str]:
        pass

    def long_params(self) -> set[str]:
        pass
