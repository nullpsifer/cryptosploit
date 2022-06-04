from modules.abstract_module import *
import cryptography.hazmat.primitives.asymmetric.dsa as cdsa
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.hashes import HashAlgorithm,SHA256
import hashlib
from utils.dsa import DSASign
from os import urandom

class SendSignature(AbstractModule):
    name = 'sendsignature'
    description = 'Send a signed message'
    arguments = [ModuleArgumentDescription('private_key','Private Signing Key', True),
                 ModuleArgumentDescription('message','Message to sign', True),
                 ModuleArgumentDescription('algorithm', 'Signature algorithm', True),
                 ModuleArgumentDescription('hashAlg', 'Hash Algorithm for the signature', True)]
    oracle = None
    oracleRequired = True

    def __init__(self):
        super().__init__()
        self.sign = {'DSA':DSASign}

    def execute(self):
        private_key = self.get_argument_value('private_key')
        p = private_key['p']
        k = int.from_bytes(urandom(p.bit_length()//8),'big') % p
        parameter_numbers = cdsa.DSAParameterNumbers(private_key['p'], private_key['q'], private_key['g'])
        public_numbers = cdsa.DSAPublicNumbers(pow(private_key['g'],private_key['x'],private_key['p']), parameter_numbers)
        privatenumbers = cdsa.DSAPrivateNumbers(private_key['x'],public_numbers)
        privatekey = privatenumbers.private_key()
        for halg in HashAlgorithm.__subclasses__():
            if halg.name == self.get_argument_value('hashAlg'):
                break

        csignature = decode_dss_signature(privatekey.sign(self.get_argument_value('message').encode('utf-8'),SHA256()))
        #hashfunction = hashlib.__dict__[self.get_argument_value('hashAlg')]
        signature = {'r':csignature[0],
                     's':csignature[1],
                     'm':self.get_argument_value('message'),
                     'hashAlgo':'sha256'}
        #signature = self.sign[self.get_argument_value('algorithm')](private_key,k,self.get_argument_value('message').encode('utf-8'),hashfunction)
        oracle = self.oracle.makeoracle()
        return oracle(signature)