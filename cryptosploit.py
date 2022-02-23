from interfaces import *
from states import AwaitingCommandState
    
def main():    
    interface = TerminalInterface(AwaitingCommandState())
    interface.handleCommands()

if __name__ == "__main__":
    main()
