import pytest

from clilib.parameters import (
    Argument,
    Flag,
    Option,
    get_param_meta,
    is_parameters,
    parameters,
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


def test_is_parameter_true():
    @parameters
    class Blank:
        ...

    assert is_parameters(Blank)


def test_is_parameters_false():
    class Blank:
        ...

    assert not is_parameters(Blank)


def test_parameter_defaults_set_when_instantiated():
    @parameters
    class Person:
        name: str = Argument("NAME", default="Mike", help="A person's name")
        age: int = Option("-o", default=42, help="A person's age")

    # Class definition doesn't have default
    assert None is Person.name
    assert None is Person.age

    p = Person()

    # Default set after instantiation
    assert "Mike" == p.name
    assert 42 == p.age


def test_child_parameter():
    @parameters
    class Child:
        name: str = Argument("NAME", default="Kara", help="A child's name")

    @parameters
    class Parent:
        name: str = Argument("NAME", default="Mike", help="A parent's name")
        child: Child

    p = Parent()

    assert isinstance(p.child, Child)
    assert "Kara" == p.child.name
