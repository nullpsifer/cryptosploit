import shlex
import pkgutil
import importlib
from modules import *
from tabulate import tabulate

version = "1.0"
modules = []
moduleClasses = None

currentModule = None

def printBanner():
    versionLine = "{0:<28}".format("Cryptosploit v" + version)
    modulesLine = "{0:<28}".format(str(len(modules)) + " modules")
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

# TODO: refactor this entire file and seperate UI rendering code from flow logic code. Most of the code in this file should be broken into seperate files.

def printHelp():
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

def getModuleList():
    global moduleClasses
    moduleClasses = AbstractModule.__subclasses__()
    for c in moduleClasses:
        modules.append([c.name, c.description])
        
def listModules(): 
    print('\n', tabulate(modules, headers=['Name', 'Description']), '\n')

def useModule(module):
    global currentModule;
    moduleClass = next((c for c in moduleClasses if c.name == module), None)
    if moduleClass == None:
        print("No module named '{}' found.\n".format(module))
    else:
        currentModule = moduleClass()

def showOptions():
    if currentModule != None:
        options = [[arg.name, arg.description, arg.required, currentModule.get_argument_value(arg.name)] for arg in currentModule.arguments]
        print('\n', tabulate(options, headers=['Name', 'Description', 'Required', 'Value']), '\n')

def setOption(optionName, optionValue):
    currentModule.set_argument_value(optionName, optionValue)

def execute():
    if not currentModule.all_required_parameters_set():
        print("Some required parameters are missing.");
        return
    currentModule.execute()
    
def handleCommands():
    while True:
        inputPrompt = None
        if currentModule != None:
            inputPrompt = 'csp({})> '.format(currentModule.name)
        else:
            inputPrompt = 'csp> '
        cmd, *args = shlex.split(input(inputPrompt))

        if cmd == 'help':
            printHelp()
        elif cmd == 'listmods':
            listModules()
        elif cmd == 'use':
            if len(args) == 0:
                printHelp()
            else:
                useModule(args[0])
        elif cmd == 'options':
            showOptions()
        elif cmd == 'set':
            if len(args) != 2:
                printHelp()
            else:
                setOption(args[0], args[1])
        elif cmd == 'execute':
            execute()
        else:
            print("Unknown command '{cmd}'. Type 'help' for help.\n\n".format(cmd=cmd))
    
def main():
    getModuleList()
    printBanner()
    handleCommands()

if __name__ == "__main__":
    main()
