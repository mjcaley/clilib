from dataclasses import dataclass
from typing import Any, Type

from .command import get_command_meta
from .parameters import Parameter, get_param_meta


class ParameterCollisionError(Exception):
    def __init__(self, collisions: set[str], message: str = None):
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


@dataclass(frozen=True)
class CommandParserContext:
    options: dict[str, ParameterMapping]
    arguments: list[ParameterMapping]
    subcommands: dict[str, Type]


@dataclass
class ParameterCompilerResult:
    options: dict[str, ParameterMapping]
    arguments: dict[str, ParameterMapping]


def compile_definitions(
    parameter: Any, definitions: dict[str, Parameter]
) -> dict[str, ParameterMapping]:
    result: dict[str, ParameterMapping] = {}
    for attr_name, definition in definitions.items():
        flattened_definitions = {
            opt_str: ParameterMapping(parameter, attr_name, definition)
            for opt_str in definition.names
        }
        if collision := result.keys() & flattened_definitions.keys():
            raise ParameterCollisionError(
                collision, f"Parameter redefined in {parameter.__class__.__name__}"
            )
        result.update(flattened_definitions)

    return result


def compile_parameter(parameter: Any) -> ParameterCompilerResult:
    options = {}
    arguments = {}

    meta = get_param_meta(parameter)

    # Compile inline options and arguments
    inline_options = compile_definitions(parameter, meta.option_defs)
    inline_arguments = compile_definitions(parameter, meta.argument_defs)

    options.update(inline_options)
    arguments.update(inline_arguments)

    # Compile all child parameter groups
    child_parameters = [getattr(parameter, pname) for pname in meta.child_params.keys()]
    child_result = compile_parameters(*child_parameters)

    options.update(child_result.options)
    arguments.update(child_result.arguments)

    return ParameterCompilerResult(options, arguments)


def compile_parameters(*parameters: Any) -> ParameterCompilerResult:
    options = {}
    arguments = {}

    for parameter in parameters:
        result = compile_parameter(parameter)

        if collision := result.options.keys() & options.keys():
            raise ParameterCollisionError(
                collision,
                f"Option redefined in child of {parameter.__class__.__qualname__}",
            )

        if collision := result.arguments.keys() & arguments.keys():
            raise ParameterCollisionError(
                collision,
                f"Argument redefined from child in {parameter.__class__.__qualname__}",
            )

        options.update(result.options)
        arguments.update(result.arguments)

    return ParameterCompilerResult(options, arguments)


def compile_command(command: Any) -> CommandParserContext:
    meta = get_command_meta(command)

    subcommands = meta.subcommands
    parameter_instances = [getattr(command, name) for name in meta.parameters.keys()]
    parameters = compile_parameters(*parameter_instances)

    return CommandParserContext(parameters.options, parameters.arguments, subcommands)
