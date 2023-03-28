from utils.binutils import RepeatedKeyXOR
from modules.abstract_module import *

class RepeatedXOR(AbstractModule):
    name = 'repeated_xor'

    description = 'This module applies a repeated xor key to an input'
    arguments = [ModuleArgumentDescription('key','XOR key', True),
                 ModuleArgumentDescription('text', 'Text to apply cipher to', True)]
    oracle = None
    oracleRequired = False

    def execute(self):
        key = self.get_argument_value('key')
        text = self.get_argument_value('text')
        xorcipher = RepeatedKeyXOR(key)
        returntext = xorcipher.crypt(text)
        return returntext
