from __future__ import annotations, print_function, unicode_literals, absolute_import

from abc import *
from tabulate import tabulate
import textwrap
import shlex
from .Interface import Interface
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
        self._commands = {'help': (lambda x: self._state.printHelp(),'', 'Display this screen.'),
                         'listmods': (lambda x: self._state.listModules(),'','List available modules.'),
                         'listor': (lambda x: self._state.listOracles(), '', 'List available oracles.'),
                         'use': (self._use,'{module}','Select module named {module} to use.'),
                         'useOracle': (self._useOracle,'{oracle}','Select oracle named {oracle} to use.'),
                         'options': (lambda x: self._printCommandResponse(self._state.showOptions()),'','Show module options and their current values.'),
                         'set': (self._set,'{option} {value}','Set {option} to {value} by name.'),
                         'copy': (self._copy,'{option}', 'Set {option} to the output of the last module'),
                         'execute': (lambda x: self._printCommandResponse(self._state.execute()),'','Execute the module.'),
                         }
            
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

    def _use(self, args):
        if len(args) != 1:
            self._state.printHelp()
            return
        self._printCommandResponse(self._state.use(args[0]))

    def _useOracle(self,args):
        if len(args) != 1:
            self._state.printHelp()
            return
        self._printCommandResponse(self._state.useOracle(args[0]))

    def _set(self,args):
        if len(args) != 2:
            self._state.printHelp()
            return
        self._state.setOption(args[0], args[1])

    def _copy(self,args):
        if len(args) != 1:
            self._state.printHelp()
            return
        self._state.copyOption(args[0])

    def _doCommand(self, cmd, *args):
        try:
            self._commands[cmd][0](args)
        except KeyError:
            print(f"Unknown command '{cmd}'. Type 'help' for help.\n\n")

    def _printCommandResponse(self, responseText):
        if responseText is not None:
            print(responseText)
        
    def showOptions(self):
        if self._module.oracle != None:
            print('\n', 'Oracle:', self._module.oracle.name, '\n\n')
        if self._module.oracle != None and self._module.oracleRequired:
            print('\nOracle (Required!): None\n\n')
        
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
        print('\n', tabulate(
            [
                [
                    textwrap.fill(f'{cmd} {self._commands[cmd][1]}',25, break_long_words=True), # command
                    textwrap.fill(self._commands[cmd][2], 50, break_long_words=False) # description
                ]
                for cmd in self._commands.keys()
            ],
            headers=['Command', 'Descriptiong']),'\n')

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