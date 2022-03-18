from clilib.command import Command
from clilib.compiler import compile_command
from clilib.parameters import Argument, Option, Parameters
from clilib.parser import Parser


def test_parse_argument(mocker):
    class Person(Parameters):
        name: str = Argument("NAME")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    p.parse_args(["Mike"])

    assert "Mike" == m.person.name


def test_parse_option(mocker):
    class Person(Parameters):
        age: int = Option("--age")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    p.parse_args(["--age", "42"])

    assert 42 == m.person.age


def test_parse_end_of_options(mocker):
    class Person(Parameters):
        name: str = Argument("NAME")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    p.parse_args(["--", "Mike"])

    assert "Mike" == m.person.name


def test_parse_subcommand(mocker):
    class Child(Command):
        ...

    class Main(Command):
        child: Child

    m = Main(context=mocker.Mock())
    compiler_result = compile_command(m)
    p = Parser(
        compiler_result.options, compiler_result.arguments, compiler_result.subcommands
    )
    result, remaining_args = p.parse_args(["child"])

    assert result is Child
