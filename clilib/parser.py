from dataclasses import dataclass
from typing import Any, Optional, Type
import sys

from .command import get_command_meta
from .parameters import Parameter, get_param_meta, is_parameters


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


class Parser:
    def __init__(
        self, options: dict[str, ParameterMapping], arguments: list[ParameterMapping], subcommands: dict[str, Type]
    ):
        self.options = options
        self.arguments = arguments
        self.subcommands = subcommands

    def parse_args(self, args: list[str] = None) -> Optional[Type]:
        if not args:
            args = sys.argv

        next_command: Optional[Type] = None
        arg_iter = iter(self.arguments.values())

        end_opts = False
        while len(args) > 0:
            current = args.pop(0)

            if not end_opts:
                if current == "--":
                    end_opts = True
                    continue

                if command_found := self.subcommands.get(current):
                    next_command = command_found
                    break

                if option := self.options.get(current):
                    value = args.pop(0)  # TODO: The argument may not take a value
                    option.set(value)
                    continue
                    # TODO: see if there's other arguments after too

            current_arg = next(arg_iter)
            current_arg.set(current)

        return next_command
