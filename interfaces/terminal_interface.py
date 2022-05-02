from __future__ import annotations, print_function, unicode_literals, absolute_import

from abc import *
from tabulate import tabulate
import textwrap
import shlex
from .interface import Interface
from states import State, AwaitingCommandState, AwaitingCommandState

try:
    import pyreadline.rlmain
    #pyreadline.rlmain.config_path=r"c:\xxx\pyreadlineconfig.ini"
    import readline, atexit
    import pyreadline.unicode_helper
    #
    #
    #Normally the codepage for pyreadline is set to be sys.stdout.encoding
    #if you need to change this uncomment the following line
    #pyreadline.unicode_helper.pyreadline_codepage="utf8"
except ImportError:
    # shhhh!
    #print("Module readline not available.")
    pass
else:
    #import tab completion functionality
    import rlcompleter

    #Override completer from rlcompleter to disable automatic ( on callable
    completer_obj = rlcompleter.Completer()
    def nop(val, word):
        return word
    completer_obj._callable_postfix = nop
    readline.set_completer(completer_obj.complete)

    #activate tab completion
    readline.parse_and_bind("tab: complete")
    readline.read_history_file()
    atexit.register(readline.write_history_file)
    del readline, rlcompleter, atexit

class TerminalInterface(Interface):

    version = "1.0"
    
    def __init__(self, state: State) -> None:
        super().__init__(state)
        self._printBanner()
            
    def _printBanner(self):
        global version
        versionLine = "{0:<28}".format("Cryptosploit v" + self.version)
        modulesLine = "{0:<28}".format(str(len(self._modules)) + " modules")
        oracleLine = "{0:<28}".format(str(len(self._oracles)) + " oracles")
        print("""\

 █▀▀ █▀█ █▄█ █▀█ ▀█▀ █▀█ █▀ █▀█ █░░ █▀█ █ ▀█▀
 █▄▄ █▀▄ ░█░ █▀▀ ░█░ █▄█ ▄█ █▀▀ █▄▄ █▄█ █ ░█░


                                               ████████                    
                                             ██        ██                  
  [ """ + versionLine + """ ]         ██            ██████████████████
  [ """ + modulesLine + """ ]         ██  ████                      ██
  [ """ + oracleLine + """ ]         ██  ████      ░░░░██░░██░░██░░██
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
        elif cmd == 'listor':
            self._state.listOracles()
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
listor                 List available oracles.
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
            
    def listOracles(self):
        print('\n', tabulate(
            [
                [
                    textwrap.fill(m[0], 25, break_long_words=True), # name
                    textwrap.fill(m[1], 50, break_long_words=False) # description
                    ]
                for m in self._oracles
                ],
            headers=['Name', 'Description']), '\n')