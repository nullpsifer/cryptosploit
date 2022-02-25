from __future__ import annotations

from abc import *
from modules import *
import pkgutil
import importlib
from states import *

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
        return self._state.use(moduleName)
        
    def set(self, varName, varValue):
        self._state.setOption(varName, varValue)
        
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