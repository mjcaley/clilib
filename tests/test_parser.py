import pytest
from clilib.command import command

from clilib.parameters import parameters, Argument, Option
from clilib.parser import (
    flatten_command_parameters,
    flatten_parameters,
    ParameterCollisionError,
)


def test_flatten_single_parameters():
    name_arg = Argument("NAME", default="Mike")
    age_opt = Option("--age")

    @parameters
    class Person:
        name = name_arg
        age: int = age_opt

    person = Person()
    result = flatten_parameters(person)

    assert person is result["NAME"].owner
    assert "name" == result["NAME"].name
    assert name_arg == result["NAME"].definition

    assert person is result["--age"].owner
    assert "age" == result["--age"].name
    assert age_opt == result["--age"].definition


def test_flatten_nested_parameters():
    child_name = Option("--child-name")
    parent_name = Option("--parent-name")

    @parameters
    class Child:
        name: str = child_name

    @parameters
    class Parent:
        name: str = parent_name
        child: Child

    parent = Parent()
    result = flatten_parameters(parent)

    assert parent is result["--parent-name"].owner
    assert "name" == result["--parent-name"].name
    assert parent_name == result["--parent-name"].definition

    assert parent.child is result["--child-name"].owner
    assert "name" == result["--child-name"].name
    assert child_name == result["--child-name"].definition


def test_flatten_raises_on_collision():
    @parameters
    class Child:
        name: str = Argument("NAME")

    @parameters
    class Parent:
        name: str = Argument("NAME")
        child: Child

    parent = Parent()

    with pytest.raises(ParameterCollisionError):
        flatten_parameters(parent)


def test_flatten_command_parameters():
    name_arg = Argument("NAME")

    @parameters
    class Person:
        name: str = name_arg

    @command
    class Main:
        person: Person

    main = Main()
    result = flatten_command_parameters(main)

    assert main.person is result["NAME"].owner
    assert "name" == result["NAME"].name
    assert name_arg == result["NAME"].definition


def test_flatten_command_parameters_collision():
    @parameters
    class Child:
        name: str = Argument("NAME")

    @parameters
    class Parent:
        name: str = Argument("NAME")

    @command
    class Main:
        parent: Parent
        child: Child

    main = Main()

    with pytest.raises(ParameterCollisionError):
        flatten_command_parameters(main)
