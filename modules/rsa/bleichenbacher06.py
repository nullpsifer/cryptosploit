from modules.abstract_module import *
from utils.bleichenbacher06 import bleichenbacher06

class Bleichenbacher06(AbstractModule):
    name = 'bleichenbacher06'

    description = 'Creates a simple Bleichenbacher06 signature'

    arguments = [ModuleArgumentDescription('bitsize','Size of the public key',True),
                 ModuleArgumentDescription('message','Message to size', True),
                 ModuleArgumentDescription('hash_function','Hash function',False, defaultValue='sha256')]
                 
    oracle = None # probably not good
    oracleRequired = True

    def execute(self):
        bitsize = int(self.get_argument_value('bitsize'))
        message = self.get_argument_value('message')
        hashfunction = self.get_argument_value('hash_function')
        data = {'m':message,'s':bleichenbacher06(bitsize,message,hashfunction)}
        respdata = self.oracle.makeoracle()(data)

        print(f'{respdata=}')
        return respdata