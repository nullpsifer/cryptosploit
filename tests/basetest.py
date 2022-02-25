import shutil
import os
import atexit
import sys
from pathlib import Path

sys.path.append('../')

from interfaces import *
from states import AwaitingCommandState

class MockInterface(Interface):

    handleCommandsCalled = False
    showOptionsCalled = False
    printHelpCalled = False
    listModulesCalled = False
    
    def handleCommands(self):
        self.handleCommandsCalled = True
 
    def showOptions(self):
        self.showOptionsCalled = True

    def printHelp(self):
        printHelpCalled = True

    def listModules(self):
        listModulesCalled = True
        
    def getState(self):
        return self._state


class BaseTest():

    interface: MockInterface = None
    
    def __init__(self):
        path = Path('mock_module.py')
        shutil.copyfile('mock_module.py', os.path.join(path.parent.absolute(), 'modules', 'mock_module.py'))
        atexit.register(self.cleanup)
        self.initialize()
        
    def initialize(self):
        self.interface = MockInterface(AwaitingCommandState())
    
    def cleanup(self):
        path = Path('mock_module.py')
        os.remove(os.path.join(path.parent.absolute(), 'modules', 'mock_module.py'))
        
    def getState(self):
        return self.interface.getState()