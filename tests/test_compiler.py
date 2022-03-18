import pytest

from clilib.compiler import (
    compile_command,
    compile_definitions,
    compile_parameter,
    compile_parameters,
    ParameterCollisionError,
)
from clilib.command import get_command_meta, Command
from clilib.parameters import get_param_meta, Parameters, Argument, Option


def test_compile_definitions():
    class Person(Parameters):
        name: str = Option("--name")
        age: int = Option("--age")

    p = Person()
    meta = get_param_meta(p)
    result = compile_definitions(p, meta.option_defs)

    assert "--name" in result
    assert "name" == result["--name"].name
    assert p is result["--name"].owner

    assert "--age" in result
    assert "age" == result["--age"].name
    assert p is result["--age"].owner


def test_compile_definitions_with_argument_collision():
    class Person(Parameters):
        first_name: str = Argument("NAME")
        last_name: str = Argument("NAME")

    p = Person()
    meta = get_param_meta(p)

    with pytest.raises(ParameterCollisionError):
        compile_definitions(p, meta.argument_defs)


def test_compile_definitions_with_option_collision():
    class Person(Parameters):
        first_name: str = Option("--name")
        last_name: str = Option("--name")

    p = Person()
    meta = get_param_meta(p)

    with pytest.raises(ParameterCollisionError):
        compile_definitions(p, meta.option_defs)


def test_compile_parameter():
    class Person(Parameters):
        name: str = Argument("NAME")
        age: int = Option("--age")

    p = Person()
    result = compile_parameter(p)

    assert "NAME" in result.arguments
    assert "name" == result.arguments["NAME"].name
    assert p is result.arguments["NAME"].owner

    assert "--age" in result.options
    assert "age" == result.options["--age"].name
    assert p is result.options["--age"].owner


def test_compile_parameter_option_collision():
    class Person(Parameters):
        first_name: str = Option("--name")
        last_name: str = Option("--name")

    p = Person()

    with pytest.raises(ParameterCollisionError):
        compile_parameter(p)


def test_compile_parameter_argument_collision():
    class Person(Parameters):
        first_name: str = Argument("NAME")
        last_name: str = Argument("NAME")

    p = Person()

    with pytest.raises(ParameterCollisionError):
        compile_parameter(p)


def test_compile_parameter_child_collision():
    class Person(Parameters):
        name: str = Option("--name")

    class Family(Parameters):
        mother: Person
        father: Person

    f = Family()

    with pytest.raises(ParameterCollisionError):
        compile_parameter(f)


def test_compile_parameters():
    class Parent(Parameters):
        name: str = Argument("PARENT_NAME")
        age: int = Option("--parent-age")

    class Child(Parameters):
        name: str = Argument("CHILD_NAME")
        age: int = Option("--child-age")

    class Family(Parameters):
        parent: Parent
        child: Child

    f = Family()
    result = compile_parameters(f)

    assert "PARENT_NAME" in result.arguments
    assert "name" == result.arguments["PARENT_NAME"].name
    assert f.parent is result.arguments["PARENT_NAME"].owner

    assert "CHILD_NAME" in result.arguments
    assert "name" == result.arguments["CHILD_NAME"].name
    assert f.child is result.arguments["CHILD_NAME"].owner

    assert "--parent-age" in result.options
    assert "age" == result.options["--parent-age"].name
    assert f.parent is result.options["--parent-age"].owner

    assert "--child-age" in result.options
    assert "age" == result.options["--child-age"].name
    assert f.child is result.options["--child-age"].owner


def test_compile_parameters_option_collision():
    class Person(Parameters):
        name: str = Option("--name")

    p1 = Person()
    p2 = Person()

    with pytest.raises(ParameterCollisionError):
        compile_parameters(p1, p2)


def test_compile_parameters_argument_collision():
    class Person(Parameters):
        name: str = Argument("NAME")

    p1 = Person()
    p2 = Person()

    with pytest.raises(ParameterCollisionError):
        compile_parameters(p1, p2)


def test_compile_command(mocker):
    class Subcommand(Command):
        ...

    class Person(Parameters):
        name: str = Argument("NAME")
        age: int = Option("--age")

    class Family(Command):
        person: Person
        subcommand: Subcommand

    f = Family(context=mocker.Mock())
    result = compile_command(f)

    assert "NAME" in result.arguments
    assert "--age" in result.options
    assert "subcommand" in result.subcommands
