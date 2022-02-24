from __future__ import annotations

from abc import *
from tabulate import tabulate
import textwrap
import shlex
from .interface import Interface
from states import State, AwaitingCommandState, AwaitingCommandState

class TerminalInterface(Interface):

    version = "1.0"
    
    def __init__(self, state: State) -> None:
        super().__init__(state)
        self._printBanner()
            
    def _printBanner(self):
        global version
        versionLine = "{0:<28}".format("Cryptosploit v" + self.version)
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