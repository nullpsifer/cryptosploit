import base64
import copy
from modules.abstract_module import *
import cryptography.hazmat.primitives.asymmetric.dsa as cdsa
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.hashes import HashAlgorithm,SHA256
from ecpy.ecdsa import ECDSA, ECPrivateKey
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto import Hash
import hashlib
from utils.dsa import DSASign
from os import urandom

hash_classes = {'SHA256': Hash.SHA256,
                'SHA224': Hash.SHA224,
                'SHA384': Hash.SHA384,
                'SHA512': Hash.SHA512,
                'keccak': Hash.keccak,
                'SHAKE256': Hash.SHAKE256}

class SendSignature(AbstractModule):
    name = 'sendsignature'
    description = 'Send a signed message'
    arguments = [ModuleArgumentDescription('private_key','Private Signing Key', True),
                 ModuleArgumentDescription('message','Message to sign', True),
                 ModuleArgumentDescription('algorithm', 'Signature algorithm', True),
                 ModuleArgumentDescription('hashAlg', 'Hash Algorithm for the signature', True),
                 ModuleArgumentDescription('encoding', 'Signature encoding {raw, binary, der}', False, defaultValue='raw'),
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
        encoding = self.get_argument_value('encoding')
        hashalg = self.get_argument_value('hashAlg')
        if isinstance(private_key,DSA.DsaKey):
            signer = DSS.new(private_key,'fips-186-3')
        else:
            signer = DSS.new(DSA.construct((private_key['y'],
                                            private_key['g'],
                                            private_key['p'],
                                            private_key['q'],
                                            private_key['x'])),'fips-186-3')
        message = self.get_argument_value('message')
        hashobj = hash_classes[hashalg].new(message.encode('utf-8'))
        signature = signer.sign(hashobj)
        sig_data= {
                     'signature':signature,
                     'm': message,
                 'hashAlgo':hashalg}

        return sig_data

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