from modules.abstractModule import *

class ExampleModule(AbstractModule):

    name = "Example Module"

    description = "This is an example module."

    arguments = [
            ModuleArgumentDescription("Arg1", "This is the first argument."),
            ModuleArgumentDescription("Arg2", "This is the second argument."),
            ModuleArgumentDescription("Arg3", "This is the third argument."),
        ]

    def execute(self):
        print("Executing...\n\n")