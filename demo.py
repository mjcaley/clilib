from heated.app import App
from heated.parameters import Parameters, Option, Argument
from heated.command import Command


class Person(Parameters):
    name: str = Argument("NAME")
    age: int = Option("--age")


class Main(Command):
    person: Person

    def invoke(self):
        print(f"My name is {self.person.name} and I am {self.person.age} years old")


app = App(Main)
app.run()
