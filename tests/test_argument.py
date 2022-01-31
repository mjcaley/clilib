import inspect

from clilib.argument import Argument, Arguments


def test_argument_class_without_args():
    class CheckArguments(Arguments):
        host = Argument("--host")
        port = Argument("--port", type_=int)

    members = inspect.getmembers(CheckArguments)

    result = CheckArguments()

    assert None is result.host
    assert None is result.port


def test_argument_class_with_args():
    class CheckArguments(Arguments):
        host = Argument("--host")
        port = Argument("--port", type_=int)

    members = inspect.getmembers(CheckArguments)

    result = CheckArguments(host="localhost", port=1783)

    assert "localhost" == result.host
    assert 1783 == result.port
