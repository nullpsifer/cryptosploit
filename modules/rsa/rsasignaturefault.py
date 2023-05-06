from utils.pkcs15 import PKCS15
from Crypto.PublicKey import RSA
from modules.abstract_module import *
from json import loads
from gmpy2 import gcd

class RSASignatureFault(AbstractModule):
    name = 'rsa_signature_fault'

    description = 'This module queries a signature oracle until it gets a repeated r value and then computes the private key'
    arguments = [ModuleArgumentDescription('public_key','Public Signing Key', True)]
    oracle = None
    oracleRequired = True

    def execute(self):
        hashfunctions = ['sha256','sha1','md5','sha384','sha512']
        keyRecovered = False
        if isinstance(self.get_argument_value('public_key'),str):
            public_key = loads(self.get_argument_value('public_key'))
        else:
            public_key = self.get_argument_value('public_key')
        e = public_key['e']
        n = public_key['n']
        privatekey = {}
        bytelength = n.bit_length()//8
        mypkcs = PKCS15(bytelength)
        while not keyRecovered:
            oracle = self.oracle.makeoracle()
            data = oracle()
            m = data['m']
            s = data['s']
            checkvalue = pow(s,e,n)
            check = checkvalue.to_bytes(bytelength,'big')
            if check[:2] != b'\x00\x01':
                for hashfunction in hashfunctions:
                    potentiallycorrectvalue = mypkcs.signaturePad(m.encode('utf-8'),hashfunction)
                    cd = int(gcd(checkvalue-potentiallycorrectvalue,n))
                    if 1 < cd < n:
                        p = cd
                        q = n//p
                        if q<p:
                            q,p=p,q
                        u=pow(p,-1,q)
                        d=pow(e,-1,(p-1)*(q-1))
                        privatekey = RSA.RsaKey(p=p,q=q,u=u,e=e,d=d,n=n)
                        print(f'Private key: {privatekey.d=}')
                        return privatekey
