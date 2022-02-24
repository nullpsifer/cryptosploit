from __future__ import annotations

from abc import *
import interfaces

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