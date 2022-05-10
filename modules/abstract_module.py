from abc import *
from typing import List
from oracles.abstract_oracle import *

class ModuleArgumentDescription():

    def __init__(self, name: str, description: str, required: bool, defaultValue=None):
        self._name = name
        self._description = description
        self._required = required
        self._defaultValue = defaultValue

    def _get_name(self):
        return self._name

    def _get_description(self):
        return self._description
        
    def _get_required(self):
        return self._required
        
    def _get_default_value(self):
        return self._defaultValue

    name = property(fget=_get_name, doc="Get name of argument.")

    description = property(fget=_get_description, doc="Get description of argument.")
    
    required = property(fget=_get_required, doc="Is this field required to run the module?")
    
    defaultValue = property(fget=_get_default_value, doc="Returns default value or None.")
    
class AbstractModule(ABC):

    name: str
    
    description: str
    
    oracle: AbstractOracle
    
    oracleRequired: bool
    
    arguments: List[ModuleArgumentDescription]
    
    def __init__(self):
        self._specified_arguments = {}
        for argumentDescription in self.__class__.arguments:
            if argumentDescription.defaultValue != None:
                self.set_argument_value(argumentDescription.name, argumentDescription.defaultValue)
        self._add_oracle_parameters()
                
    def _add_oracle_parameters(self):
        if self.oracle:
            for arg in self.oracle.arguments:
                self.arguments.append(ModuleArgumentDescription('o:' + arg.name, arg.description, arg.required, arg.defaultValue))
                
    def _remove_oracle_parameters(self):
        if self.oracle:
            for arg in self.oracle.arguments:
                nameToRemove = 'o:' + arg.name
                self.arguments = list(filter(lambda existingArg: existingArg.name != nameToRemove, self.arguments))

    def get_module_information(self):
        return self._module_information

    def get_argument_value(self, argumentName):
        """ Returns current value of specified argument. """
        if not argumentName in self._specified_arguments:
            return None
        return self._specified_arguments[argumentName]        

    def set_argument_value(self, argumentName, value):
        """ Sets argument to given value. """
        if argumentName.startswith('o:'):
            self._specified_arguments[argumentName] = value
            self.oracle.set_argument_value(argumentName, value)
        else:
            self._specified_arguments[argumentName] = value
        
    def all_required_parameters_set(self):
        if self.oracleRequired and not self.oracle:
            return False
        if self.oracle:
            if not self.oracle.all_required_parameters_set():
                return False
        for argumentDescription in self.__class__.arguments:
            if argumentDescription.required and argumentDescription.name not in self._specified_arguments:
                return False
        return True

    @abstractmethod
    def execute(self):
        """ Executes the module with the set arguments. """
        pass
