import pytest

from heated.compiler import (
    CompilerStore,
    CompilerStoreBool,
    CompilerArgument,
    CompilerOption,
    compile_command,
    compile_parameters,
    ParameterCollisionError,
)
from heated.command import Command
from heated.parameters import (
    Flag,
    flatten_parameters,
    Parameters,
    Argument,
    Option,
)


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


def test_compile_parameters_single_argument(mocker):
    class Person(Parameters):
        name: str = Argument("NAME")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    flattened_parameters = flatten_parameters(m.person)
    result = compile_parameters(flattened_parameters)

    action = result[0][0].action
    assert isinstance(action, CompilerStore)
    assert m.person is action.owner
    assert "name" == action.member_name
    assert str is action.type_


def test_compile_parameters_single_option(mocker):
    class Person(Parameters):
        name: str = Option("--name")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    flattened_parameters = flatten_parameters(m.person)
    result = compile_parameters(flattened_parameters)

    action = result[1]["--name"].child
    assert isinstance(action, CompilerStore)
    assert m.person is action.owner
    assert "name" == action.member_name
    assert str is action.type_


def test_compile_parameters_single_flag(mocker):
    class Person(Parameters):
        alive: str = Flag("--alive")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    flattened_parameters = flatten_parameters(m.person)
    result = compile_parameters(flattened_parameters)

    action = result[1]["--alive"].child
    assert isinstance(action, CompilerStoreBool)
    assert m.person is action.owner
    assert "alive" == action.member_name


def test_compile_command(mocker):
    class Person(Parameters):
        name: str = Option("--name")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    result = compile_command(m)

    assert True


def test_compile_collision(mocker):
    class Parent(Parameters):
        name: str = Option("--name")

    class Child(Parameters):
        name: str = Option("--name")

    class Family(Command):
        parent: Parent
        child: Child

    f = Family(context=mocker.Mock())
    
    with pytest.raises(ParameterCollisionError):
        compile_command(f)
