from clilib.command import CommandMeta, command, get_command_meta, is_command
from clilib.parameters import Argument, parameters


def test_is_command_true():
    @command
    class Main:
        ...

    assert is_command(Main)


def test_is_command_false():
    class Main:
        ...

    assert not is_command(Main)


def test_get_command_meta():
    @command
    class Main:
        ...

    result = get_command_meta(Main)

    assert isinstance(result, CommandMeta)


def test_subcommand_types_saved():
    @command
    class Child:
        ...

    @command
    class Main:
        child: Child

    assert Child == get_command_meta(Main).subcommands["child"]


def test_parameter_type_saved():
    @parameters
    class Param:
        ...

    @command
    class Main:
        param: Param

    assert Param == get_command_meta(Main).parameters["param"]


def test_default_configuration():
    @command
    class Command_Name:
        ...

    assert (
        Command_Name.__name__.lower().replace("_", "-")
        == get_command_meta(Command_Name).name
    )


def test_set_name():
    @command(name="main-command")
    class Main:
        ...

    assert "main-command" == get_command_meta(Main).name


def test_instantiate_with_parameters():
    @parameters
    class Person:
        name: str = Argument("--name", "-n", default="Mike")

    @command
    class Main:
        person: Person

    main = Main()

    assert "Mike" == main.person.name
