import shlex
import pkgutil
import importlib
from modules import *
from tabulate import tabulate

def printBanner(version, onlineAttacks, offlineAttacks):
    versionLine = "{0:<28}".format("Cryptosploit v" + version)
    onlineAttackLine = "{0:<28}".format(str(onlineAttacks) + " online attacks")
    offlineAttackLine = "{0:<28}".format(str(offlineAttacks) + " offline attacks")
    print("""\

 █▀▀ █▀█ █▄█ █▀█ ▀█▀ █▀█ █▀ █▀█ █░░ █▀█ █ ▀█▀
 █▄▄ █▀▄ ░█░ █▀▀ ░█░ █▄█ ▄█ █▀▀ █▄▄ █▄█ █ ░█░


                                               ████████                    
                                             ██        ██                  
  [ """ + versionLine + """ ]         ██            ██████████████████
  [ """ + onlineAttackLine + """ ]         ██  ████                      ██
  [ """ + offlineAttackLine + """ ]         ██  ████      ░░░░██░░██░░██░░██
  [ github.com/cryptosploit      ]         ██░░        ░░████  ██  ██  ██  
                                             ██░░░░░░░░██                  
                                               ████████                    

        """)

# TODO: refactor this entire file and seperate UI rendering code from flow logic code. Most of the code in this file should be broken into seperate files.

def printHelp():
    print("\n\n> Help here. <\n\n")
       
def listModules():
    modules = []
    moduleClasses = AbstractModule.__subclasses__()
    for c in moduleClasses:
        modules.append([c.name, c.description])
    print('\n', tabulate(modules, headers=['Name', 'Description']), '\n')

def handleCommands():
    while True:
        # TODO: add module name to input prompt if finite state machine allows it
        # csp(someattack)>
        cmd, *args = shlex.split(input('csp> '))

        # TODO: implement state machine to track which commands are currently available
        # https://refactoring.guru/design-patterns/state
        if cmd == 'help':
            printHelp()
        elif cmd == 'listmods':
            listModules()
        else:
            print("Unknown command '{cmd}'. Type 'help' for help.\n\n".format(cmd=cmd))
    
def main():
    # TODO: get module counts here, should probably preload info for getModules()
    printBanner("1.0", 10, 12)
    handleCommands()

if __name__ == "__main__":
    main()
