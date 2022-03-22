import pytest

from heated.parameters import (
    Argument,
    Flag,
    FlatParameter,
    Option,
    Parameters,
    flatten_parameters,
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
    assert "name" in meta.definitions
    assert Parent.name is meta.definitions["name"]
    assert "age" in meta.definitions
    assert Parent.age is meta.definitions["age"]
    assert Child is meta.child_parameters["child"]


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


def test_flatten_parameters_single():
    class Parent(Parameters):
        name: str = Argument("NAME")
        age: int = Option("--name")

    p = Parent()
    result = flatten_parameters(p)

    assert p is result[0].owner
    assert "name" == result[0].member_name
    assert Parent.name is result[0].parameter

    assert p is result[1].owner
    assert "age" == result[1].member_name
    assert Parent.age is result[1].parameter


def test_flatten_parameters_multiple():
    class Parent(Parameters):
        name: str = Argument("PARENT_NAME")
        age: int = Option("--parent-name")

    class Child(Parameters):
        name: str = Argument("CHILD_NAME")
        age: int = Option("--child-name")

    p = Parent()
    c = Child()
    result = flatten_parameters(p, c)

    assert p is result[0].owner
    assert "name" == result[0].member_name
    assert Parent.name is result[0].parameter

    assert p is result[1].owner
    assert "age" == result[1].member_name
    assert Parent.age is result[1].parameter

    assert c is result[2].owner
    assert "name" == result[2].member_name
    assert Child.name is result[2].parameter

    assert c is result[3].owner
    assert "age" == result[3].member_name
    assert Child.age is result[3].parameter


def test_flatten_parameters_nested():
    class Child(Parameters):
        name: str = Argument("CHILD_NAME")
        age: int = Option("--child-name")

    class Parent(Parameters):
        child: Child

    p = Parent()
    result = flatten_parameters(p)

    assert p.child is result[0].owner
    assert "name" == result[0].member_name
    assert Child.name is result[0].parameter

    assert p.child is result[1].owner
    assert "age" == result[1].member_name
    assert Child.age is result[1].parameter
