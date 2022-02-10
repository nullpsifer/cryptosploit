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
    print("\n\n> Help here. <\n\n")

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
        currentModule = moduleClass

def showOptions():
    pass
    
def handleCommands():
    while True:
        # TODO: add module name to input prompt if finite state machine allows it
        # csp(someattack)>
        inputPrompt = None
        if currentModule != None:
            inputPrompt = 'csp({})> '.format(currentModule.name)
        else:
            inputPrompt = 'csp> '
        cmd, *args = shlex.split(input(inputPrompt))

        # TODO: implement state machine to track which commands are currently available
        # https://refactoring.guru/design-patterns/state
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
        else:
            print("Unknown command '{cmd}'. Type 'help' for help.\n\n".format(cmd=cmd))
    
def main():
    getModuleList()
    printBanner()
    handleCommands()

if __name__ == "__main__":
    main()
