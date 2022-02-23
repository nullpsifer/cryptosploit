from __future__ import annotations

import shlex
import pkgutil
import importlib
from modules import *
from tabulate import tabulate
import textwrap

from abc import *

version = "1.0"

class Interface(ABC):

    _state = None
    _module = None
    _modules = []
    _moduleClasses = None

    def __init__(self, state: State) -> None:
        self.setState(state)
        self._getModuleList()
    
    def setState(self, state: State):
        self._state = state
        self._state.interface = self
        
    def _getModuleList(self):
        self._moduleClasses = AbstractModule.__subclasses__()
        for c in self._moduleClasses:
            self._modules.append([c.name, c.description])

    def use(self, moduleName):
        self._state.use(moduleName)
        
    def set(self, varName, varValue):
        self._state.use(varName, varValue)
        
    def execute(self):
        self._state.execute()
        
    @abstractmethod
    def handleCommands(self):
        pass
 
    @abstractmethod
    def showOptions(self):
        pass

    @abstractmethod
    def printHelp(self):
        pass

    @abstractmethod
    def listModules(self):
        pass
        
    @property
    def module(self) -> AbstractModule:
        return self._module
        
    @module.setter
    def module(self, module: AbstractModule) -> None:
        self._module = module
        
    @property
    def moduleClasses(self):
        return self._moduleClasses
        
    @property
    def modules(self):
        return self._modules
     
class TerminalInterface(Interface):
    
    def __init__(self, state: State) -> None:
        super().__init__(state)
        self._printBanner()
            
    def _printBanner(self):
        versionLine = "{0:<28}".format("Cryptosploit v" + version)
        modulesLine = "{0:<28}".format(str(len(self._modules)) + " modules")
        print("""\

 █▀▀ █▀█ █▄█ █▀█ ▀█▀ █▀█ █▀ █▀█ █░░ █▀█ █ ▀█▀
 █▄▄ █▀▄ ░█░ █▀▀ ░█░ █▄█ ▄█ █▀▀ █▄▄ █▄█ █ ░█░


                                               ████████                    
                                             ██        ██                  
  [ """ + versionLine + """ ]         ██            ██████████████████
  [ """ + modulesLine + """ ]         ██  ████                      ██
                                           ██  ████      ░░░░██░░██░░██░░██
                                           ██░░        ░░████  ██  ██  ██  
                                             ██░░░░░░░░██                  
                                               ████████                    

""")

    def handleCommands(self):
        while True:
            inputPrompt = None
            if self._module != None:
                inputPrompt = 'csp({})> '.format(self._module.name)
            else:
                inputPrompt = 'csp> '
            readInput = input(inputPrompt)
            if not readInput or not readInput.strip():
                continue
            cmd, *args = shlex.split(readInput)
            self._doCommand(cmd, *args) 
        
    def _doCommand(self, cmd, *args):
        if cmd == 'help':
            self._state.printHelp()
        elif cmd == 'listmods':
            self._state.listModules()
        elif cmd == 'use':
            if len(args) == 0:
                self._state.printHelp()
            else:
                self._printCommandResponse(self._state.use(args[0]))
        elif cmd == 'options':
            self._printCommandResponse(self._state.showOptions())
        elif cmd == 'set':
            if len(args) != 2:
                self._state.printHelp()
            else:
                self._state.setOption(args[0], args[1])
        elif cmd == 'execute':
            self._printCommandResponse(self._state.execute())
        else:
            print("Unknown command '{cmd}'. Type 'help' for help.\n\n".format(cmd=cmd))

    def _printCommandResponse(self, responseText):
        if responseText is not None:
            print(responseText)
        
    def showOptions(self):
        if self._module != None:
            options = [
                [
                    textwrap.fill(arg.name, 15, break_long_words=True),
                    textwrap.fill(arg.description, 35, break_long_words=False),
                    arg.required,
                    textwrap.fill(
                        '' if self._module.get_argument_value(arg.name) == None
                        else str(self._module.get_argument_value(arg.name)),
                        20, break_long_words=True)
                    ]
                for arg in self._module.arguments
                ]
            print('\n', tabulate(options, headers=['Name', 'Description', 'Required', 'Value']), '\n')
            
    def printHelp(self):
        print("""\

 Command                Description
---------------------  -----------------------------------------------

help                   Display this screen.
listmods               List available modules.
use {module}           Select module named {module} to use.
options                Show module options and their current values.
set {option} {value}   Set option to value by name.
execute                Execute the module.

""")

    def listModules(self):
        print('\n', tabulate(
            [
                [
                    textwrap.fill(m[0], 25, break_long_words=True), # name
                    textwrap.fill(m[1], 50, break_long_words=False) # description
                    ]
                for m in self._modules
                ],
            headers=['Name', 'Description']), '\n')

class State(ABC):

    @property
    def interface(self) -> Interface:
        return self._interface
        
    @interface.setter
    def interface(self, interface: Interface) -> None:
        self._interface = interface
        
    @abstractmethod
    def setOption(self, optionName, optionValue) -> str:
        pass
        
    @abstractmethod
    def execute(self) -> str:
        pass
        
    @abstractmethod
    def showOptions(self):
        pass
        
    def use(self, moduleName) -> str:
        moduleClass = next((c for c in self.interface.moduleClasses if c.name == moduleName), None)
        if moduleClass == None:
            return "No module named '{}' found.\n".format(moduleName)
        else:
            self.interface.module = moduleClass()

        self._interface.setState(ModuleSelectedState())
            
    def listModules(self):
        self.interface.listModules()
            
    def printHelp(self):
        self.interface.printHelp()

class AwaitingCommandState(State):
        
    def setOption(self, optionName, optionValue) -> str:
        return "No module selected."
        
    def execute(self) -> str:
        return "No module selected."
        
    def showOptions(self):
        pass

class ModuleSelectedState(State):
        
    def setOption(self, optionName, optionValue) -> str:
        self.interface.module.set_argument_value(optionName, optionValue)
        if self.interface.module.all_required_parameters_set():
            self._interface.setState(ReadyToExecuteState())
        
    def execute(self) -> str:
        return "Some required parameters are missing."
        
    def showOptions(self):
        self.interface.showOptions()

class ReadyToExecuteState(State):
        
    def setOption(self, optionName, optionValue) -> str:
        self.interface.module.set_argument_value(optionName, optionValue) 
        
    def execute(self) -> str:
        self.interface.module.execute()
        
    def showOptions(self):
        self.interface.showOptions()
    
def main():    
    interface = TerminalInterface(AwaitingCommandState())
    interface.handleCommands()

if __name__ == "__main__":
    main()
