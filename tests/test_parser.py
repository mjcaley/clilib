from clilib.command import command

from clilib.command import command
from clilib.compiler import compile_command
from clilib.parameters import Argument, Option, parameters
from clilib.parser import Parser


def test_parse_argument():
    @parameters
    class Person:
        name: str = Argument("NAME")

    @command
    class Main:
        person: Person

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
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
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    p.parse_args(["--age", "42"])

    assert 42 == m.person.age


def test_parse_end_of_options():
    @parameters
    class Person:
        name: str = Argument("NAME")

    @command
    class Main:
        person: Person

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    p.parse_args(["--", "Mike"])

    assert "Mike" == m.person.name


def test_parse_subcommand():
    @command
    class Child:
        ...

    @command
    class Main:
        child: Child

    m = Main()
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    result = p.parse_args(["child"])

    assert result is Child
