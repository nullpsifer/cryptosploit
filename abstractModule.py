from abc import *
from typing import List

class ModuleArgumentDescription():

    def _init_(self, name: str, description: str):
        self._name = name
        self._description = description

    def _get_name(self):
        return self._name

    def _get_description(self):
        return self._description

    name = property(fget=_get_name, doc="Get name of argument.")

    description = property(fget=_get_description, doc="Get description of argument.")
    
class ModuleInformation():

    def __init__(self, name: str, description: str, arguments: List[ModuleArgumentDescription]):
        self._module_name = name
        self._module_description = description
        self._arguments = arguments

    def _get_module_name(self):
        return self._module_name

    def _get_module_description(self):
        return self._module_description

    def _get_arguments(self):
        return self._arguments

    module_name = property(fget=_get_module_name, doc="Get module name.")

    module_description = property(fget=_get_module_description, doc="Get module description.")

    module_arguments = property(fget=_get_arguments, doc="Get list of arguments with descriptions.")
    
class AbstractModule(ABC):

    def __init__(self, moduleInformation: ModuleInformation):
        self._module_information = moduleInformation
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
