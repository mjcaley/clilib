import pytest

from clilib.parameters import (
    Argument,
    Flag,
    Option,
    Parameters,
    get_param_meta,
    is_parameters,
)


@pytest.fixture
def help_message():
    return "Help message"


def test_option(help_message):
    o = Option("-s", "--long", default="default", help=help_message)

    assert "-s" in o.names
    assert "--long" in o.names
    assert "default" == o.default
    assert help_message == o.help


def test_argument(help_message):
    a = Argument("-s", "--long", default="default", help=help_message)

    assert "-s" in a.names
    assert "--long" in a.names
    assert "default" == a.default
    assert help_message == a.help


def test_flag(help_message):
    f = Flag("-s", "--long", default=True, help=help_message)

    assert "-s" in f.names
    assert "--long" in f.names
    assert True is f.default
    assert help_message == f.help


def test_parameters_meta():
    class Child(Parameters):
        ...

    class Parent(Parameters):
        name: str = Argument("NAME")
        age: int = Option("--age")
        child: Child

    p = Parent()
    meta = get_param_meta(p)

    assert "parent" == meta.name
    assert "name" in meta.argument_defs
    assert Parent.name is meta.argument_defs["name"]
    assert "age" in meta.option_defs
    assert Parent.age is meta.option_defs["age"]
    assert Child is meta.child_params["child"]


def test_parameters_name():
    class Parent(Parameters, name="mike"):
        ...

    meta = get_param_meta(Parent)

    assert "mike" == meta.name


def test_is_parameters_true():
    class Blank(Parameters):
        ...

    b = Blank()
    result = is_parameters(b)

    assert result


def test_is_parameters_false():
    class Blank:
        ...

    b = Blank()
    result = is_parameters(b)

    assert not result


def test_parameter_defaults_to_none():
    class Person(Parameters):
        name: str = Argument("NAME")

    p = Person()

    assert None is p.name


def test_parameter_defaults_set_when_instantiated():
    class Person(Parameters):
        name: str = Argument("NAME", default="Mike", help="A person's name")
        age: int = Option("-o", default=42, help="A person's age")

    p = Person()

    assert "Mike" == p.name
    assert 42 == p.age


def test_child_parameter():
    class Child(Parameters):
        name: str = Argument("NAME", default="Kara", help="A child's name")

    class Parent(Parameters):
        name: str = Argument("NAME", default="Mike", help="A parent's name")
        child: Child

    p = Parent()

    assert "Kara" == p.child.name


def test_inherited_parameters():
    class ParentName(Parameters):
        name: str = Argument("NAME", default="Mike")

    class ChildName(Parameters):
        name: str = Argument("NAME", default="Kara")

    class Person(ParentName, ChildName):
        ...

    p = Person()

    assert "Mike" == p.name
