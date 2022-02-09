from abc import *
from typing import List

class ModuleArgumentDescription():

    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description

    def _get_name(self):
        return self._name

    def _get_description(self):
        return self._description

    name = property(fget=_get_name, doc="Get name of argument.")

    description = property(fget=_get_description, doc="Get description of argument.")
    
class AbstractModule(ABC):

    module_name: str
    
    module_description: str
    
    module_arguments: List[ModuleArgumentDescription]
    
    def __init__(self):
        self._arguments = {}

    def get_module_information(self):
        return self._module_information

    def get_argument_value(self, argumentName):
        """ Returns current value of specified argument. """
        return self._arguments[argumentName]

    def set_argument_value(self, argumentName, value):
        """ Sets argument to given value. """
        self._arguments[argumentName] = value

    @abstractmethod
    def execute(self):
        """ Executes the module with the set arguments. """
        pass
