import base64
import copy
from modules.abstract_module import *
import cryptography.hazmat.primitives.asymmetric.dsa as cdsa
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.hashes import HashAlgorithm,SHA256
from ecpy.ecdsa import ECDSA, ECPrivateKey
import hashlib
from utils.dsa import DSASign
from os import urandom

class SendSignature(AbstractModule):
    name = 'sendsignature'
    description = 'Send a signed message'
    arguments = [ModuleArgumentDescription('private_key','Private Signing Key', True),
                 ModuleArgumentDescription('message','Message to sign', True),
                 ModuleArgumentDescription('algorithm', 'Signature algorithm', True),
                 ModuleArgumentDescription('hashAlg', 'Hash Algorithm for the signature', True),
                 ModuleArgumentDescription('include_public_key', 'Flag to include public key', False, defaultValue='False'),
                 ModuleArgumentDescription('include_params', 'Flag to include key parameters', False, defaultValue='False')]
    oracle = None
    oracleRequired = True

    def __init__(self):
        super().__init__()
        self.sign = {'DSA':self._dsasign,
                     'ECDSA':self._ecdsa}

    def _dsasign(self):
        private_key = self.get_argument_value('private_key')
        p = private_key['p']
        k = int.from_bytes(urandom(p.bit_length()//8),'big') % p
        parameter_numbers = cdsa.DSAParameterNumbers(private_key['p'], private_key['q'], private_key['g'])
        public_numbers = cdsa.DSAPublicNumbers(pow(private_key['g'],private_key['x'],private_key['p']), parameter_numbers)
        privatenumbers = cdsa.DSAPrivateNumbers(private_key['x'],public_numbers)
        privatekey = privatenumbers.private_key()
        for halg in HashAlgorithm.__subclasses__():
            print(halg.name)
            if halg.name == self.get_argument_value('hashAlg'):
                break

        csignature = decode_dss_signature(privatekey.sign(self.get_argument_value('message').encode('utf-8'),halg()))
        #hashfunction = hashlib.__dict__[self.get_argument_value('hashAlg')]
        signature = {'r':csignature[0],
                     's':csignature[1],
                     'm':self.get_argument_value('message'),
                     'hashAlgo':halg.name}
        return signature
        #signature = self.sign[self.get_argument_value('algorithm')](private_key,k,self.get_argument_value('message').encode('utf-8'),hashfunction)

    def _ecdsa(self):
        private_key = self.get_argument_value('private_key')
        message = self.get_argument_value('message')
        if isinstance(private_key,ECPrivateKey):
            public_key = private_key.get_public_key()
            signer = ECDSA()
            signature = base64.b16encode(signer.sign(message.encode('utf-8'),private_key)).decode('utf-8')
            data = {'signature':signature,'m':message}
            if self.get_argument_value('include_public_key') == 'True':
                data['pubkey'] = (public_key.W.x, public_key.W.y)
            if self.get_argument_value('include_params') == 'True':
                domain = copy.copy(public_key.W.curve._domain)
                domain['generator'] = (domain['generator'].x,domain['generator'].y)
                data['params'] = domain
        return data

    def execute(self):
        oracle = self.oracle.makeoracle()
        signature = self.sign[self.get_argument_value('algorithm')]()
        print(signature)
        return oracle(signature)