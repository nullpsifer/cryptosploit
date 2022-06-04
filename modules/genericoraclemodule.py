from modules.abstract_module import *

class GenericOracleModule(AbstractModule):

    name = 'generic_oracle_module'
    description = 'This module runs an oracle and returns the result'
    arguments = []
    oracle = None
    oracleRequired = True

    def execute(self):
        oracle = self.oracle.makeoracle()
        return oracle()

