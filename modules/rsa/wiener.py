from cryptography import x509
from modules.abstract_module import *
from utils.wiener import wiener_attack
from json import loads
from gmpy2 import gcd
from Crypto.PublicKey import RSA
class Wiener(AbstractModule):
    name = 'wiener_attack'

    description = "This module attempts to run Wiener's attack on a public key"
    arguments = [ModuleArgumentDescription('public_keys','Public Keys', True)]
    oracle = None
    oracleRequired = False

    def execute(self):
        def handlekey(input):
            if input.__class__.__name__ == 'Certificate':
                public_key = input.public_key()
                public_numbers = public_key.public_numbers()
                e, n = public_numbers.e, public_numbers.n
            elif isinstance(input, dict):
                e, n = input['e'], input['n']
            return e,n

        inputs = self.get_argument_value('public_keys')
        privatekeys = []
        if isinstance(inputs,list):
            for input in inputs:
                e,n = handlekey(input)
                print(f'{e=} {n=}')
                p,q,d = wiener_attack(e,n)
                u=pow(p,-1,q)
                privatekeys.append(RSA.RsaKey(p=p,q=q,d=d,u=u,e=e,n=n))
        else:
            e, n = handlekey(inputs)
            print(f'{e=} {n=}')
            p, q, d = wiener_attack(e, n)
            u = pow(p, -1, q)
            privatekeys.append(RSA.RsaKey(p=p, q=q, d=d, u=u, e=e, n=n))

        print(f'Private keys: {privatekeys}')
        return privatekeys
