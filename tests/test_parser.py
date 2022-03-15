import pytest
from clilib.command import command

from clilib.command import command
from clilib.parameters import Argument, Option, get_param_meta, parameters
from clilib.parser import (
    CommandParserContext,
    ParameterCollisionError,
    Parser,
    compile_command,
    compile_definitions,
    compile_parameters,
    compile_parameter,
)


def test_compile_definitions():
    @parameters
    class Person:
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
    @parameters
    class Person:
        first_name: str = Argument("NAME")
        last_name: str = Argument("NAME")

    p = Person()
    meta = get_param_meta(p)

    with pytest.raises(ParameterCollisionError):
        compile_definitions(p, meta.argument_defs)


def test_compile_definitions_with_option_collision():
    @parameters
    class Person:
        first_name: str = Option("--name")
        last_name: str = Option("--name")

    p = Person()
    meta = get_param_meta(p)

    with pytest.raises(ParameterCollisionError):
        compile_definitions(p, meta.option_defs)


def test_compile_parameter():
    @parameters
    class Person:
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
    @parameters
    class Person:
        first_name: str = Option("--name")
        last_name: str = Option("--name")

    p = Person()

    with pytest.raises(ParameterCollisionError):
        compile_parameter(p)


def test_compile_parameter_argument_collision():
    @parameters
    class Person:
        first_name: str = Argument("NAME")
        last_name: str = Argument("NAME")

    p = Person()

    with pytest.raises(ParameterCollisionError):
        compile_parameter(p)


def test_compile_parameter_child_collision():
    @parameters
    class Person:
        name: str = Option("--name")

    @parameters
    class Family:
        mother: Person
        father: Person

    f = Family()

    with pytest.raises(ParameterCollisionError):
        compile_parameter(f)


def test_compile_parameters():
    @parameters
    class Parent:
        name: str = Argument("PARENT_NAME")
        age: int = Option("--parent-age")

    @parameters
    class Child:
        name: str = Argument("CHILD_NAME")
        age: int = Option("--child-age")

    @parameters
    class Family:
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
    @parameters
    class Person:
        name: str = Option("--name")

    p1 = Person()
    p2 = Person()
    
    with pytest.raises(ParameterCollisionError):
        compile_parameters(p1, p2)


def test_compile_parameters_argument_collision():
    @parameters
    class Person:
        name: str = Argument("NAME")

    p1 = Person()
    p2 = Person()
    
    with pytest.raises(ParameterCollisionError):
        compile_parameters(p1, p2)


def test_compile_command():
    @command
    class Subcommand: ...

    @parameters
    class Person:
        name: str = Argument("NAME")
        age: int = Option("--age")

    @command
    class Family:
        person: Person
        subcommand: Subcommand

    f = Family()
    result = compile_command(f)

    assert "NAME" in result.arguments
    assert "--age" in result.options
    assert "subcommand" in result.subcommands


def test_parse_argument():
    @parameters
    class Person:
        name: str = Argument("NAME")

    @command
    class Main:
        person: Person

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(compiler_result.options, compiler_result.arguments, compiler_result.subcommands)
    p.parse_args(["Mike"])

    assert "Mike" == m.person.name


def test_parse_option():
    @parameters
    class Person:
        age: int = Option("--age")

    @command
    class Main:
        person: Person

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(compiler_result.options, compiler_result.arguments, compiler_result.subcommands)
    p.parse_args(["--age", "42"])

    assert "42" == m.person.age


def test_parse_end_of_options():
    @parameters
    class Person:
        name: str = Argument("NAME")

    @command
    class Main:
        person: Person

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(compiler_result.options, compiler_result.arguments, compiler_result.subcommands)
    p.parse_args(["--", "Mike"])

    assert "Mike" == m.person.name


def test_parse_subcommand():
    @command
    class Child: ...

    @command
    class Main:
        child: Child

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(compiler_result.options, compiler_result.arguments, compiler_result.subcommands)
    result = p.parse_args(["child"])

    assert result is Child
