from modules.abstract_module import *
from utils.paddingoracle import PaddingOracleAttack
import hashlib

class PasswordCrackModule(AbstractModule):
    name = 'password_crack'

    description = 'Runs through a wordlist of possible passwords'

    arguments = [ModuleArgumentDescription('ciphertext','Ciphertext to decrypt',True),
                 ModuleArgumentDescription('wordlist', 'Path to wordlist', True),
                 ModuleArgumentDescription('keyfunction', 'Function for key derivation function', True),
                 ModuleArgumentDescription('checkstring', "A string expected in the platintext", False, defaultValue=None)]
                 
    oracle = None
    oracleRequired = True

    def execute(self):
        ciphertext = self.get_argument_value('ciphertext')
        wordlist = self.get_argument_value('wordlist')
        checkstring = self.get_argument_value('checkstring')
        keyfunction = hashlib.__dict__[self.get_argument_value('keyfunction')]

        oracle = self.oracle.makeoracle()
        with open(wordlist) as f:
            words = [w.strip() for w in f.readlines()]

        for password in words:
            plaintext = oracle(ciphertext, keyfunction(password.encode('utf-8')).hexdigest())
            if checkstring.encode('utf-8') in plaintext:
                print(f'{plaintext=}')
                return password
        print('Failed to find a valid password')
        return ''
