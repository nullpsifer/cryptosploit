from modules.abstract_module import *
from utils.paddingoracle import PaddingOracleAttack

class PaddingOracleModule(AbstractModule):
    name = 'padding_oracle_attack'

    description = 'Runs a CBC Padding Oracle Attack'

    arguments = [ModuleArgumentDescription('ciphertext','Ciphertext to decrypt',True)]
                 
    oracle = None
    oracleRequired = True

    def execute(self):
        ciphertext = self.get_argument_value('ciphertext')

        poa = PaddingOracleAttack(ciphertext,self.oracle.makeoracle())
        plaintext = poa.runattack()
        print(f'{plaintext=}')
        return plaintext
