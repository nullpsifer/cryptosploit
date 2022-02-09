from ..abstractModule import *

class ExampleModule(AbstractModule):

    name = "Example Module"

    description = "This is an example module."

    arguments = [
            ModuleArgumentDescription("Arg1", "This is the first argument."),
            ModuleArgumentDescription("Arg2", "This is the second argument."),
            ModuleArgumentDescription("Arg3", "This is the third argument."),
        ]

    def __init__(self):
        Base.__init__(self, ModuleInformation(name, description, arguments))

    def execute(self):
        print("Executing...\n\n")