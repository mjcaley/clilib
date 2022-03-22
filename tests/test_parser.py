from clilib.command import Command
from clilib.compiler import compile_command
from clilib.parameters import Argument, Flag, Option, Parameters
from clilib.parser import Parser


def test_parse_option(mocker):
    class Person(Parameters):
        name: str = Option("--name")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiled = compile_command(m)
    result_command, result_remaining_args = Parser.parse_args(compiled, ["--name", "Mike"])

    assert None is result_command
    assert 0 == len(result_remaining_args)
    assert "Mike" == m.person.name


def test_parse_flag(mocker):
    class Person(Parameters):
        alive: bool = Flag("--alive")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiled = compile_command(m)
    result_command, result_remaining_args = Parser.parse_args(compiled, ["--alive"])

    assert None is result_command
    assert 0 == len(result_remaining_args)
    assert m.person.alive


def test_parse_argument(mocker):
    class Person(Parameters):
        name: str = Argument("NAME")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiled = compile_command(m)
    result_command, result_remaining_args = Parser.parse_args(compiled, ["Mike"])

    assert None is result_command
    assert 0 == len(result_remaining_args)
    assert "Mike" == m.person.name


def test_parse_end_opts(mocker):
    class Person(Parameters):
        name: str = Argument("NAME")

    class Main(Command):
        person: Person

    m = Main(context=mocker.Mock())
    compiled = compile_command(m)
    result_command, result_remaining_args = Parser.parse_args(compiled, ["--", "Mike"])

    assert None is result_command
    assert 0 == len(result_remaining_args)
    assert "Mike" == m.person.name


def test_parse_subcommand(mocker):
    class ChildParams(Parameters):
        name: str = Option("--name")

    class Child(Command): ...

    class Main(Command):
        child: Child

    m = Main(context=mocker.Mock())
    compiled = compile_command(m)
    result_command, result_remaining_args = Parser.parse_args(compiled, ["child", "--name", "Kara"])

    assert Child is result_command
    assert ["--name", "Kara"] == result_remaining_args
