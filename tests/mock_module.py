from modules.abstract_module import *

class MockModule(AbstractModule):

    executed = False
    
    name = "mock_module"

    description = "Module for testing purposes."

    arguments = [
            ModuleArgumentDescription("Arg1", "Argument 1", True),
            ModuleArgumentDescription("Arg2", "Argument 2", False),
            ModuleArgumentDescription("Arg3", "Argument 3", False)
        ]

    def execute(self):
        self.executed = True