from modules.abstract_module import *
from json import dumps

class CryptoHackChainOfFools(AbstractModule):
    name = 'cryptohack_cof'

    description = 'This module takes new private keys and executes against Crypto Hack Chain of Fools challenge'
    arguments = [ModuleArgumentDescription('private_keys','Private Keys', True),
                 ModuleArgumentDescription('host', 'Host for the cert to attack', False, defaultValue='www.bing.com')]
    oracle = None
    oracleRequired = True

    def execute(self):
        private_keys = self.get_argument_value('private_keys')
        host = self.get_argument_value('host')
        private_key, public_key = private_keys[host]
        curve = public_key.curve.name.replace('CoF','')
        generator = public_key.curve.generator
        oracle = self.oracle.makeoracle()
        packet = {'host':host,
                  'private_key':private_key,
                  'curve':curve,
                  'generator':(generator.x, generator.y)
                  }
        print(packet)
        return oracle(dumps(packet).encode('utf-8'),True)
