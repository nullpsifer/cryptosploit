from modules.abstract_module import *
from utils.BleichenbacherPaddingOracle import BleichenbacherPOA

class BleichenbacherPaddingOracleModule(AbstractModule):
    name = 'bleichenbacher_padding_oracle'

    description = 'Runs a Bleichenbacher Padding Oracle Attack'

    arguments = [ModuleArgumentDescription('ciphertext','Ciphertext to decrypt',True),
                 ModuleArgumentDescription('publickey','Public Key', True)]
                 
    oracle = None # probably not good
    oracleRequired = True

    def execute(self):
        ciphertext = int(self.get_argument_value('ciphertext'),16)
        public_key = self.get_argument_value('publickey')

        poa = BleichenbacherPOA(public_key['n'], public_key['e'], ciphertext, self.oracle.makeoracle())
        plaintext = poa.run()
        print(f'{plaintext=}')
        return plaintext