from __future__ import annotations

from abc import *
import interfaces
from icecream import ic
import socket
import glob
import os

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
    def copyOption(self, optionName) -> str:
        pass

    @abstractmethod
    def openFile(self, filename) -> str:
        pass

    def openSocket(self, host, port) -> str:
        newsocket = socket.socket()
        newsocket.connect((host,port))
        socketId = min(range(self.interface.maxsockID+1) - self.interface.sockets.keys())
        self.interface.sockets[socketId] = (host,int(port),newsocket)
        if socketId == self.interface.maxsockID:
            self.interface.maxsockID += 1
        return f'Socket {socketId} connected to {host}:{port}'

    def closeSocket(self, socketIDs) -> str:
        for socketID in socketIDs:
            try:
                socketTuple = self._interface.sockets[int(socketID)]
            except KeyError:
                print(f'Invalid socketID')
                continue
            socketTuple[-1].close()
            del self._interface.sockets[int(socketID)]
            return 'Sockets closed'

    def listSockets(self,socketIDs):
        if len(socketIDs) == 0:
            socketIDs = self._interface.sockets.keys()
        for socketID in socketIDs:
            print(f'Socket {socketID} connected to {self._interface.sockets[socketID][0]}:{self._interface.sockets[socketID][1]}')

    @abstractmethod
    def writeFile(self, filename) -> str:
        pass

    @abstractmethod
    def useOracle(self, oracleName) -> str:
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
        
    def useOracle(self, oracleName) -> str:
        oracleClass = next((c for c in self.interface.oracleClasses if c.name == oracleName), None)
        if oracleClass == None:
            return "No oracle named '{}' found.\n".format(oracleName)
        else:
            self.interface.module._remove_oracle_parameters()
            self.interface.module.oracle = oracleClass()
            self.interface.module.oracle.sockets = self.interface.sockets
            self.interface.module._add_oracle_parameters()

        self._interface.setState(ModuleSelectedState())
            
    def listModules(self):
        self.interface.listModules()
        
    def listOracles(self):
        self.interface.listOracles()
            
    def printHelp(self):
        self.interface.printHelp()
        
class AwaitingCommandState(State):
        
    def setOption(self, optionName, optionValue) -> str:
        return "No module selected."

    def copyOption(self, optionName) -> str:
        return 'No module selected'

    def openFile(self, args) -> str:
        filetype = args[0]
        filenames = []
        for arg in args[1:]:
            filenames += glob.glob(arg)
        filedata = [self.interface._filetypes_open[filetype](filename) for filename in filenames]
        if len(filedata) == 1:
            filedata = filedata[0]
        self._interface._returnvalue = filedata
        return None

    def writeFile(self, filename) -> str:
        return 'No module selected'

    def useOracle(self, oracleName) -> str:
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

    def copyOption(self, optionName):
        self.setOption(optionName, self.interface.returnvalue)

    def openFile(self, args):
        filetype = args[0]
        filenames = []
        for arg in args[1:]:
            filenames += glob.glob(arg)
        filedata = [self.interface._filetypes_open[filetype](filename) for filename in filenames]
        if len(filedata) == 1:
            filedata = filedata[0]
        self._interface._returnvalue = filedata

    def writeFile(self,args):
        filetype = args[0]
        filename, extension = os.path.splitext(args[1])
        returnvalue = self._interface._returnvalue
        if isinstance(returnvalue, list) and len(returnvalue) > 1:
            for i in range(len(returnvalue)):
                self._interface._filetypes_write[filetype](f'{filename}{i}.{extension}', returnvalue[i])
            return None
        if isinstance(returnvalue,list):
            self._interface._filetypes_write[filetype](f'{filename}.{extension}', returnvalue[0])
            return None
        self._interface._filetypes_write[filetype](f'{filename}.{extension}', returnvalue)
        return None

    def useOracle(self, oracleName) -> str:
        oracleClass = next((c for c in self.interface.oracleClasses if c.name == oracleName), None)
        if oracleClass == None:
            return "No oracle named '{}' found.\n".format(oracleName)
        else:
            self.interface.module.oracle = oracleClass()
            self.interface.module.oracle.sockets = self.interface.sockets
            self.interface.module._remove_oracle_parameters()
            self.interface.module._add_oracle_parameters()

        self._interface.setState(ModuleSelectedState())

    def execute(self) -> str:
        return "Some required parameters are missing."
        
    def showOptions(self):
        self.interface.showOptions()
        
class ReadyToExecuteState(State):
        
    def setOption(self, optionName, optionValue) -> str:
        self.interface.module.set_argument_value(optionName, optionValue)

    def copyOption(self, optionName):
        self.setOption(optionName, self.interface.returnvalue)

    def openFile(self, args):
        filetype = args[0]
        filenames = []
        for arg in args[1:]:
            filenames += glob.glob(arg)
        filedata = [self.interface._filetypes_open[filetype](filename) for filename in filenames]
        if len(filedata) == 1:
            filedata = filedata[0]
        self._interface._returnvalue = filedata

    def writeFile(self,args):
        filetype = args[0]
        filename, extension = os.path.splitext(args[1])
        returnvalue = self._interface._returnvalue
        if isinstance(returnvalue, list) and len(returnvalue) > 1:
            for i in range(len(returnvalue)):
                self._interface._filetypes_write[filetype](f'{filename}{i}{extension}', returnvalue[i])
            return None
        if isinstance(returnvalue,list):
            self._interface._filetypes_write[filetype](f'{filename}{extension}', returnvalue[0])
            return None
        self._interface._filetypes_write[filetype](f'{filename}{extension}', returnvalue)
        return None

    def execute(self) -> str:
        try:
            self._interface._returnvalue = self.interface.module.execute()
            return self.interface.returnvalue
        except KeyboardInterrupt:
            print('Keyboard Interrupt requested')
            return None
        
    def showOptions(self):
        self.interface.showOptions()