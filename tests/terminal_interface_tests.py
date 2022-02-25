import unittest
from basetest import *

class TerminalInterfaceTests(unittest.TestCase, BaseTest):
        
    def test_cannot_execute_when_no_module_selected(self):
        self.initialize()
        self.interface.execute()
        self.assertNotEqual(type(self.getState()).__name__, 'ReadyToExecuteState')

    # Work in progress
    def test_use_changes_state(self):
        self.initialize()
        print(self.interface.use('mock_module'))
        self.assertEqual(type(self.getState()).__name__, 'ModuleSelectedState')

    # Work in progress
    def test_can_execute_when_required_parameters_present(self):
        self.initialize()
        self.interface.use('mock_module')
        self.interface.set('Arg1','lol')
        self.interface.execute()
        self.assertEqual(type(self.getState()).__name__, 'ReadyToExecuteState')

if __name__ == '__main__':
	unittest.main()
