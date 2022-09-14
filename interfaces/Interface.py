from __future__ import annotations

import logging
from abc import *
from modules import *
import pkgutil
import importlib
from states import *
from oracles import *

class Interface(ABC):

    _state = None
    _module = None
    _modules = []
    _moduleClasses = None
    _oracles = []
    _oracleClasses = None
    _returnvalue = None
    _continueLoop = True

    def __init__(self, state: State) -> None:
        logging.basicConfig(filename='cryptosploit.log', encoding='utf-8', level=logging.DEBUG)
        self.setState(state)
        self._getModuleList()
        self._getOracleList()

    def setState(self, state: State):
        self._state = state
        self._state.interface = self
        
    def _getModuleList(self):
        self._moduleClasses = AbstractModule.__subclasses__()
        for c in self._moduleClasses:
            pythonmodule = c.__module__.split('.')[1:-1]
            self._modules.append(['.'.join(pythonmodule+[c.name]), c.description])
            
    def _getOracleList(self):
        self._oracleClasses = AbstractOracle.__subclasses__()
        for c in self._oracleClasses:
            self._oracles.append([c.name, c.description])

    def use(self, moduleName):
        return self._state.use(moduleName)
        
    def useOracle(self, moduleName):
        return self._state.useOracle(moduleName)
        
    def set(self, varName, varValue):
        self._state.setOption(varName, varValue)

    def copy(self, varName):
        self._state.setOption(varName,self._state.interface.returnvalue)
        
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
        
    @abstractmethod
    def listOracles(self):
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

    @property
    def oracleClasses(self):
        return self._oracleClasses

    @property
    def oracles(self):
        return self._oracles

    @property
    def continueLoop(self):
        return self._continueLoop

    @module.setter
    def continueLoop(self,continueLoop: bool) -> None:
        self._continueLoop = continueLoop

    @property
    def returnvalue(self):
        return self._returnvalue
