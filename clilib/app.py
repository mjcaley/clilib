from typing import Type

from .context import Context


class App:
    def __init__(self, entry_command: Type = None, context: Context = None):
        self.entry_command = entry_command
        self.context = context

    def run(self):
        # Create default context
        # Instantiate the entry command, passing the context
        # Have entry Command parse the arguments
        # Return value will be remaining parsed arguments, next Command, and Argument instance
        # If parsed arguments is empty, call the entry Command's invoke method
        # If parsed arguments isn't empty, and there's a next Command, loop at Command instantiation

        context = self.Meta.context or Context()
        command = self.default_command(context=context)
        result = command.invoke()
