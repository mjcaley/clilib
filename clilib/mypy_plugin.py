from typing import Callable, Optional, Type

from mypy.nodes import AssignmentStmt, NameExpr, Var
from mypy.plugin import AnalyzeTypeContext, ClassDefContext, FunctionContext, Plugin
from mypy.types import Type, get_proper_type


class CliGenMyPyPlugin(Plugin):
    # def get_attribute_hook(self, fullname: str):
    #     print("attr hook", fullname)

    # def get_class_decorator_hook(self, fullname: str):
    #     print("class decorator", fullname)

    # def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], Type]]:
    #     parameter_names = ["clilib.parameters.Argument", "clilib.parameters.Option"]
    #     if fullname in parameter_names:
    #         print("Function hook hit", fullname)
    #         return parameter_attribute_hook

    # def get_type_analyze_hook(self, fullname: str) -> Optional[Callable[[AnalyzeTypeContext], Type]]:
    #     if "parameters" in fullname:
    #         print(fullname)

    def get_class_decorator_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname == "clilib.parameters.parameters":
            print(fullname)
            return parameter_decorator_hook


def parameter_decorator_hook(ctx):
    # print(dir(ctx))

    cls = ctx.cls
    print(f"Starting class {cls.name}")

    for stmt in ctx.cls.defs.body:
        breakpoint()
        print("Statement enter")
        if not isinstance(stmt, AssignmentStmt):
            continue

        lhs = stmt.lvalues[0]
        if not isinstance(lhs, NameExpr):
            continue

        sym = cls.info.names.get(lhs.name)
        print(f"Attribute name {sym}")
        if sym is None:
            continue
        print("Statement end")

        node = sym.node
        if not isinstance(node, Var):
            continue

        # Not needed?
        node_type = get_proper_type(node.type)

        


# def parameter_attribute_hook(ctx):
#     breakpoint()
#     print(dir(ctx))


def plugin(version: str):
    return CliGenMyPyPlugin
