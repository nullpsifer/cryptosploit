from __future__ import annotations, print_function, unicode_literals, absolute_import

import socket
from abc import *

import Crypto.IO.PEM
from cryptography import x509
import logging
import json
from tabulate import tabulate
import textwrap
import shlex
from .Interface import Interface
from states import State, AwaitingCommandState, AwaitingCommandState
from Crypto.PublicKey import RSA, DSA, ECC

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, load_ssh_public_key, load_ssh_private_key, load_der_private_key, load_der_public_key
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, ed448

import readline, atexit
import re
import os

RE_SPACE = re.compile('.*\s+$', re.M)
KEY_TYPES = (RSA.RsaKey, DSA.DsaKey, ECC.EccKey)
class Completer(object):
    # This is based on the code found at https://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input

    def __init__(self, terminal_interface):
        self.interface = terminal_interface

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _filetype(self, filetype_prefix=None):
        if filetype_prefix:
            return [filetype+' ' for filetype in self.interface._filetypes_open.keys() if filetype.startswith(filetype_prefix)]
        return list(self.interface._filetypes_open.keys())

    def _filetype_write(self, filetype_prefix=None):
        if filetype_prefix:
            return [filetype+' ' for filetype in self.interface._filetypes_write.keys() if filetype.startswith(filetype_prefix)]
        return list(self.interface._filetypes_write.keys())

    def _complete_path(self, path=None, extensions=None):
        "Perform completion of filesystem path."
        if not path:
            res = self._listdir('.')
        else:
            dirname, rest = os.path.split(path)
            tmp = dirname if dirname else '.'
            res = [os.path.join(dirname, p)
                    for p in self._listdir(tmp) if p.startswith(rest)]
        if extensions:
            res = [path for path in res if os.path.isdir(path) or os.path.splitext(path)[-1] in extensions]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']


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

    def complete_copy(self, args):
        if not args:
            return [option.name + ' ' for option in self.interface._module.arguments]
        return [option.name + ' ' for option in self.interface._module.arguments if option.name.startswith(args[-1])]

    def complete_closeSocket(self, args):
        if not args:
            return [f'{socketID} ' for socketID in self.interface.sockets.keys()]
        return [f'{socketID} ' for socketID in self.interface.sockets.keys() if f'{socketID}'.startswith(args[-1])]

    def complete_listSockets(self, args):
        if not args:
            return [f'{socketID} ' for socketID in self.interface.sockets.keys()]
        return [f'{socketID} ' for socketID in self.interface.sockets.keys() if f'{socketID}'.startswith(args[-1])]

    def complete_open(self, args):
        if len(args) < 2:
            return self._filetype(args[0])
        if [''] == args[1:]:
            return self._complete_path(extensions=self.interface._filetypes_extensions[args[0]])
        return self._complete_path(args[-1],extensions=self.interface._filetypes_extensions[args[0]])

    def complete_write(self, args):
        if len(args) < 2:
            return self._filetype_write(args[0])
        if [''] == args[1:]:
            return self._complete_path()
        return self._complete_path(args[-1])


    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        if not line:
            return [c + ' ' for c in self.interface._commands.keys()][state]
        if RE_SPACE.match(buffer):
            line.append('')
        cmd = line[0].strip()
        if cmd in self.interface._commands_fixed_num_args and len(line[1:]) > self.interface._commands_fixed_num_args[cmd]:
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
        self.sockets = {}
        self.maxsockID = 0
        self._printBanner()
        self._commands_fixed_num_args = {'use':1,
                                         'useOracle':1,
                                         'set':1,
                                         'copy':1}
        self._filetypes_open = {'raw' : self._raw_file,
                           'json' : self._json_file,
                           'pem_public_key' : self._pem_public_key,
                           'pem_private_key' : self._pem_private_key,
                           'x509_der_cert' : self._x509_der_cert_file,
                           'x509_pem_cert' : self._x509_pem_cert_file,
                           'der_public_key' : self._der_public_key,
                           'der_private_key' : self._der_private_key,
                           'ssh_public_key' : self._ssh_public_key,
                           'ssh_private_key' : self._ssh_private_key,
                                }

        self._filetypes_extensions = {'raw' : None,
                                'json' : ['.json'],
                                'pem_public_key' : ['.pem'],
                                'pem_private_key' : ['.pem', '.key'],
                                'x509_der_cert' : ['.der', '.cer'],
                                'x509_pem_cert' : ['.pem','.crt', '.cer', '.ca-bundle'],
                                'der_public_key' : ['.der', '.cer'],
                                'der_private_key' : ['.der','.key'],
                                'ssh_public_key' : ['.pub'],
                                'ssh_private_key' : [''],
                                }

        self._filetypes_write = {'raw' : self._raw_file_write,
                                'json' : self._json_file_write,
                                'pem_public_key' : self._pem_public_key_write,
                                'pem_private_key' : self._pem_private_key_write,
                                'x509_der_cert' : self._x509_der_cert_file_write,
                                'x509_pem_cert' : self._x509_pem_cert_file_write,
                                'der_public_key' : self._der_public_key_write,
                                'der_private_key' : self._der_private_key_write,
                                'ssh_public_key' : self._ssh_public_key_write,
                                }
        self._commands = {'help': (lambda x: self._state.printHelp(),'', 'Display this screen.'),
                         'listmods': (lambda x: self._state.listModules(),'','List available modules.'),
                         'listor': (lambda x: self._state.listOracles(), '', 'List available oracles.'),
                         'use': (self._use,'{module}','Select module named {module} to use.'),
                         'useOracle': (self._useOracle,'{oracle}','Select oracle named {oracle} to use.'),
                         'options': (lambda x: self._printCommandResponse(self._state.showOptions()),'','Show module options and their current values.'),
                         'set': (self._set,'{option} {value}','Set {option} to {value} by name.'),
                         'copy': (self._copy,'{option}', 'Set {option} to the output of the last module'),
                         'execute': (lambda x: self._printCommandResponse(self._state.execute()),'','Execute the module.'),
                         'open': (self._open,'{filetype} {filename}','Open and read {filename}'),
                         'write': (self._write,'{filetype} {filename}','Write {filename} and convert to {filetype} if necessary'),
                         'openSocket': (self._openSocket,'{host} {port}','Open TCP/IP socket to {host}:{port}'),
                         'closeSocket': (self._closeSocket,'{socketID}','Close socket {socketID}'),
                         'listSockets': (self._listSockets, '{socketIDs}', 'List information about sockets. If IDs are specified, just those sockets, otherwise, all sockets'),
                         'display': (lambda x: self._display(), '', 'Display the returned value from the last command'),
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
            readline.write_history_file(histfile)

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
            except EOFError:
                self._exit()
            if not readInput or not readInput.strip():
                continue
            cmd, *args = shlex.split(readInput)
            self._doCommand(cmd, *args) 

    def _display(self):
        displayvalue = self.returnvalue
        if isinstance(displayvalue,rsa._RSAPublicKey):
            print(f'RSA Public Key:\ne={displayvalue.public_numbers().e}\nn={displayvalue.public_numbers().n}')
        if isinstance(displayvalue, rsa._RSAPrivateKey):
            print(f'RSA Public Key:\ne={displayvalue.public_key().public_numbers().e}\nn={displayvalue.public_key().public_numbers().n}\nd={displayvalue.private_numbers().d}\np={displayvalue.private_numbers().p}\nq={displayvalue.private_numbers().q}\ndmp1={displayvalue.private_numbers().dmp1}\ndmq1={displayvalue.private_numbers().dmq1}\niqmp={displayvalue.private_numbers().iqmp}')
        elif isinstance(displayvalue, RSA.RsaKey) and displayvalue.has_private():
            output = f'RSA Private Key:\ne={displayvalue.e}\nn={displayvalue.n}\nd={displayvalue.d}\np={displayvalue.p}\nq={displayvalue.q}\n'
            print(output)
        else:
            print(displayvalue)

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

    def _open(self,args):
        if len(args) < 2:
            self._state.printHelp()
            return
        self._state.openFile(args)

    def _openSocket(self,args):
        if len(args) != 2:
            self._state.printHelp()
            return
        self._state.openSocket(args[0],int(args[1]))

    def _closeSocket(self,args):
        if len(args)<1:
            self._state.printHelp()
            return
        self._state.closeSocket(args)

    def _listSockets(self,args):
        self._state.listSockets(args)

    def _write(self,args):
        if len(args) != 2:
            self._state.printHelp()
            return
        self._state.writeFile(args)

    def _raw_file(self,filename):
        with open(filename, 'rb') as f:
            return f.read()

    def _raw_file_write(self,filename,data):
        print(f'We got the following kind of data to write: {data}')
        with open(filename, 'wb') as f:
            f.write(data)

    def _public_key_write(self, filename, key, fileformat):
        assert isinstance(key,KEY_TYPES)
        key = key.public_key()
        with open(filename, 'wb') as f:
            try:
                f.write(key.export_key(fileformat))
            except ValueError:
                print(f'Unable to write public key {key} as {fileformat} to {filename}')
            return None

    def _private_key_write(self, filename, key, fileformat):
        assert isinstance(key,KEY_TYPES) and key.has_private()
        with open(filename, 'wb') as f:
            try:
                f.write(key.export_key(fileformat))
            except ValueError:
                print(f'Unable to write private key {key} as {fileformat} to {filename}')
            return None

    def _x509_der_cert_file(self,filename):
        with open(filename, 'rb') as f:
            try:
                cert = x509.load_der_x509_certificate(f.read())
            except ValueError:
                print('Unable to open cert')
                cert = None
            return cert

    def _x509_der_cert_file_write(self,filename,cert):
        print('Currently unimplemented')
        return None

    def _x509_pem_cert_file(self,filename):
        with open(filename, 'rb') as f:
            try:
                cert = x509.load_pem_x509_certificate(f.read())
            except ValueError:
                print('Unable to open cert')
                cert = None
            return cert

    def _x509_pem_cert_file_write(self,filename,cert):
        print('Currently unimplemented')
        return None

    def _json_file(self,filename):
        with open(filename, 'rb') as f:
            return json.loads(f.read())

    def _json_file_write(self,filename,data):
        with open(filename, 'wb') as f:
            try:
                f.write(json.dumps(data))
            except:
                print('Failed to dump data as json to file')
        return None

    def _pem_public_key(self,filename):
        with open(filename, 'rb') as f:
            try:
                public_key = load_pem_public_key(f.read())
            except ValueError as e:
                print(f'Unable to load public key: {e}')
                public_key = None
            return public_key

    def _pem_public_key_write(self,filename, public_key):
        return self._public_key_write(filename, public_key, 'PEM')

    def _pem_private_key(self,filename, password=None):
        with open(filename, 'rb') as f:
            try:
                private_key = load_pem_private_key(f.read(), password)
            except ValueError:
                print('Unable to open private key')
                private_key = None
            return private_key

    def _pem_private_key_write(self,filename, key):
        return self._private_key_write(filename,key,'PEM')

    def _der_public_key(self,filename):
        with open(filename, 'rb') as f:
            try:
                public_key = load_der_public_key(f.read())
            except ValueError:
                print('Unable to load public key')
                public_key = None
            return public_key

    def _der_public_key_write(self,filename,key):
        return self._public_key_write(filename,key,'DER')

    def _der_private_key(self, filename):
        with open(filename, 'rb') as f:
            try:
                private_key = load_der_private_key(f.read())
            except ValueError:
                print('Unable to load private key')
                private_key = None
            return private_key

    def _der_private_key_write(self, filename, key):
        return self._private_key_write(filename,key,'DER')

    def _ssh_public_key(self, filename):
        with open(filename, 'rb') as f:
            try:
                public_key = load_ssh_public_key(f.read())
            except ValueError:
                print('Unable to load ssh public key')
                public_key=None
            return public_key

    def _ssh_public_key_write(self, filename, key):
        return self._public_key_write(filename,key,'OpenSSH')

    def _ssh_private_key(self, filename):
        with open(filename, 'rb') as f:
            return load_ssh_private_key(f.read())

    def _exit(self):
        print('Exiting...')
        self.continueLoop = False
        quit()

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
        except KeyError as e:
            print(f"Unknown command '{cmd}'. Type 'help' for help.\n\n")
            print(f'KeyException {e}')

        except Exception as e:
            print('Error: exception encountered')
            logging.exception(str(e))
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
                        '' if self._module.get_argument_value(arg.name) is None
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

