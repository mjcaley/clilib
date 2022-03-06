from clilib.command import command
from clilib.parameters import parameters, Argument


def test_internals_exist():
    @command
    class Main: ...

    assert hasattr(Main, "_parameters")
    assert hasattr(Main, "_subcommands")
    assert hasattr(Main, "_commandconfig")


def test_subcommand_types_saved():
    @command
    class Child: ...
    
    @command
    class Main:
        child: Child

    assert Child == Main._subcommands["child"]


def test_parameter_type_saved():
    @parameters
    class Param: ...

    @command
    class Main:
        param: Param

    assert Param == Main._parameters["param"]


def test_default_configuration():
    @command
    class Main: ...

    assert None is Main._commandconfig["name"]


def test_set_name():
    @command(name="main")
    class Main: ...

    assert "main" == Main._commandconfig["name"]


def test_instantiate_with_parameters():
    @parameters
    class Person:
        name: str = Argument("--name", "-n", default="Mike")    
    
    @command
    class Main:
        person: Person

    main = Main()

    assert "Mike" == main.person.name
