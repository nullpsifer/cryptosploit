from __future__ import annotations, print_function, unicode_literals, absolute_import

from abc import *
import logging
from tabulate import tabulate
import textwrap
import shlex
from .Interface import Interface
from states import State, AwaitingCommandState, AwaitingCommandState

import readline, atexit
import re

RE_SPACE = re.compile('.*\s+$', re.M)
class Completer(object):

    def __init__(self, terminal_interface):
        self.interface = terminal_interface

    def complete_use(self, args):
        if not args:
            return [mod[0] + ' ' for mod in self.interface._modules]
        return [mod[0] + ' ' for mod in self.interface._modules if mod[0].startswith(args[-1])]

    def complete_useOracle(self, args):
        if not args:
            return [oracle[0] + ' ' for oracle in self.interface._oracles]
        return [oracle[0] + ' ' for oracle in self.interface._oracles if oracle[0].startswith(args[-1])]

    def complete_set(self, args):
        if not args:
            return [option.name + ' ' for option in self.interface._module.arguments]
        return [option.name + ' ' for option in self.interface._module.arguments if option.name.startswith(args[-1])]

    def complete_set(self, args):
        if not args:
            return [option.name + ' ' for option in self.interface._module.arguments]
        return [option.name + ' ' for option in self.interface._module.arguments if option.name.startswith(args[-1])]

    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        if not line:
            return [c + ' ' for c in self.interface._commands.keys()][state]
        if RE_SPACE.match(buffer):
            line.append('')
        cmd = line[0].strip()
        if len(line)>2:
            return ([]+[None])[state]
        if cmd in set(self.interface._commands.keys()):
            impl = getattr(self, f'complete_{cmd}')
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            if len([c for c in self.interface._commands.keys() if c.startswith(cmd)]) == 1:
                return [cmd + ' '][state]
        results = [c + ' ' for c in self.interface._commands.keys() if c.startswith(cmd)] + [None]
        return results[state]



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
                         'exit': (lambda x: self._exit(), '', 'Exits cryptosploit')
                         }
            
    def _printBanner(self):
        global version
        versionLine = f'{"Cryptosploit v" + self.version:<28}'
        modulesLine = f'{str(len(self._modules)) + " modules":<28}'
        oracleLine = f'{str(len(self._oracles)) + " oracles":<28}'
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
        comp = Completer(self)
        readline.set_completer_delims(' \t\n')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(comp.complete)
        histfile = '.cryptosploit.history'
        try:
            readline.read_history_file(histfile)
            h_len = readline.get_current_history_length()
        except FileNotFoundError:
            open(histfile, 'wb').close()
            h_len = 0

        def save(prev_h_len, histfile):
            new_h_len = readline.get_current_history_length()
            readline.set_history_length(1000)
            readline.append_history_file(new_h_len - prev_h_len, histfile)

        atexit.register(save, h_len, histfile)
        readInput = ''
        while self._continueLoop:
            modifyPrompt = ''
            if self._module != None:
                if self._module.oracle != None:
                    modifyPrompt = f'({self._module.name}:{self._module.oracle.name})'
                else:
                    modifyPrompt = f'({self._module.name})'

            inputPrompt = f'csp{modifyPrompt}> '
            try:
                readInput = input(inputPrompt)
            except KeyError:
                print(f"Unknown command '{cmd}'. Type 'help' for help.\n\n")
            except EOFError:
                self._exit()
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

    def _exit(self):
        print('Exiting...')
        self.continueLoop = False

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
            print(f'Unknown command: {cmd}')

        except Exception as e:
            print('Error: exception encountered')
            logging.error(str(e))
        return


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
            headers=['Command', 'Description']),'\n')

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

