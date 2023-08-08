import utils.dsa as dsa
from Crypto.PublicKey import DSA
from hashlib import sha256
from modules.abstract_module import *
from json import loads

class KnownNonceDSa(AbstractModule):
    name = 'known_nonce'

    description = 'This module queries a signature oracle until it gets a repeated r value and then computes the private key'
    arguments = [ModuleArgumentDescription('public_key','Public Signing Key', True)]
    oracle = None
    oracleRequired = True

    def execute(self):
        if isinstance(self.get_argument_value('public_key'),str):
            public_key = loads(self.get_argument_value('public_key'))
        else:
            public_key = self.get_argument_value('public_key')
        q = public_key['q']
        oracle = self.oracle.makeoracle()
        data = oracle()
        h = int.from_bytes(sha256(data['m'].encode('utf-8')).digest(),'big')
        k = data['k']
        r = data['r']
        s = data['s']
        print(dsa.DSAVerify(public_key,data))
        x = dsa.known_nonce(k,h,s,r,q)
        g = public_key['g']
        p = public_key['p']
        y = public_key['y']
        if y != pow(g,x,p):
            print('[-]Incorrect private key computed!!!')
        print(f'Private key: {x}')
        return DSA.construct((y,g,p,q,x))
