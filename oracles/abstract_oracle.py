from abc import *
from typing import List

class OracleArgumentDescription():

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
    
    required = property(fget=_get_required, doc="Is this field required to run the oracle?")
    
    defaultValue = property(fget=_get_default_value, doc="Returns default value or None.")
    
class AbstractOracle(ABC):

    name: str
    
    description: str
    
    arguments: List[OracleArgumentDescription]

    sockets : dict
    
    def __init__(self):
        self._specified_arguments = {}
        for argumentDescription in self.__class__.arguments:
            if argumentDescription.defaultValue != None:
                self.set_argument_value(argumentDescription.name, argumentDescription.defaultValue)

    def get_oracle_information(self):
        return self._oracle_information

    def get_argument_value(self, argumentName):
        """ Returns current value of specified argument. """
        if not argumentName in self._specified_arguments:
            return None
        return self._specified_arguments[argumentName]

    def set_argument_value(self, argumentName, value):
        """ Sets argument to given value. """
        self._specified_arguments[argumentName] = value
        
    def all_required_parameters_set(self):
        for argumentDescription in self.__class__.arguments:
            if argumentDescription.required and argumentDescription.name not in self._specified_arguments:
                return False
        return True

    @abstractmethod
    def makeoracle(self):
        """ Executes the oracle with the set arguments. """
        pass
