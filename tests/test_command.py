from clilib.command import Command, CommandMeta, get_command_meta, is_command
from clilib.parameters import Argument, Parameters


def test_is_command_true():
    class Main(Command):
        ...

    assert is_command(Main)


def test_is_command_false():
    class Main:
        ...

    assert not is_command(Main)


def test_get_command_meta():
    class Main(Command):
        ...

    result = get_command_meta(Main)

    assert isinstance(result, CommandMeta)


def test_subcommand_types_saved():
    class Child(Command):
        ...

    class Main(Command):
        child: Child

    assert Child == get_command_meta(Main).subcommands["child"]


def test_parameter_type_saved():
    class Param(Parameters):
        ...

    class Main(Command):
        param: Param

    assert Param == get_command_meta(Main).parameters["param"]


def test_default_configuration():
    class Command_Name(Command):
        ...

    assert (
        Command_Name.__name__.lower().replace("_", "-")
        == get_command_meta(Command_Name).name
    )


def test_set_name():
    class Main(Command, name="main-command"):
        ...

    assert "main-command" == get_command_meta(Main).name


def test_instantiate_with_parameters(mocker):
    class Person(Parameters):
        name: str = Argument("--name", "-n", default="Mike")

    class Main(Command):
        person: Person

    main = Main(context=mocker.Mock())

    assert "Mike" == main.person.name
