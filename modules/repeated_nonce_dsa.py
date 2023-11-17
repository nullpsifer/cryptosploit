import utils.dsa as dsa
from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey
from ecpy.formatters import encode_sig
from ecpy.ecdsa import ECDSA
from tqdm import tqdm
from modules.abstract_module import *
from Crypto.PublicKey import DSA
from utils.dict2key import dict2publickey

class RepeatedNonceDSa(AbstractModule):
    name = 'repeated_nonce'

    description = 'This module queries a signature oracle until it gets a repeated r value and then computes the private key'
    arguments = [ModuleArgumentDescription('public_key','Public Signing Key', False, defaultValue=None),
                 ModuleArgumentDescription('parameters','Parameters, either the name of a curve or comma separated p,q,g values', False,defaultValue=None)]
    oracle = None
    oracleRequired = True

    def execute(self):
        t = tqdm()
        public_key = None
        is_EC = False
        if self.get_argument_value('public_key') != None:
            if isinstance(self.get_argument_value('public_key'),str):
                public_key = dict2publickey(loads(self.get_argument_value('public_key')))
            elif isinstance(self.get_argument_value('public_key'),dict):
                public_key = dict2publickey(self.get_argument_value('public_key'))
            else:
                public_key = self.get_argument_value('public_key')
            if not isinstance(public_key,(DSA.DsaKey,Point)):
                print(f'[-] Invalid Key {public_key=}')
            if isinstance(public_key, Point):
                is_EC = True
                curve = public_key.curve
            else:
                g,p,q = public_key.g,public_key.p,public_key.q
        else:
            try:
                p,q,g = map(int,self.get_argument_value('parameters').split(','))
            except ValueError:
                curve = Curve.get_curve(self.get_argument_value('parameters'))
                is_EC = True
                if curve == None:
                    print('No public key or valid parameters provided')
                    return None

        if is_EC:
            group_order = curve.order
        else:
            group_order = q
        collected_signatures = dict({})
        oracle = self.oracle.makeoracle()
        print('Collecting Signatures')
        while True:
            signature = oracle()
            if signature['r'] in collected_signatures.keys():
                r = signature['r']
                s1 = signature['s']
                h1 = signature['h']
                s2 = collected_signatures[signature['r']]['s']
                h2 = collected_signatures[signature['r']]['h']
                x = dsa.repeated_nonce(h1,s1,r,h2,s2,group_order)
                if is_EC:
                    private_key = ECPrivateKey(x, curve)
                    signer = ECDSA()
                    if signer.verify(h.to_bytes(r.bit_length() // 8, 'big'), encode_sig(r, s),
                                     private_key.get_public_key()):
                        print('Verified private key by using the corresponding public key and verified the signature')
                    else:
                        x=dsa.repeated_nonce(h1,s1,r,h2,-s2,group_order)
                        private_key = ECPrivateKey(x, curve)
                        signer = ECDSA()
                        if signer.verify(h.to_bytes(r.bit_length() // 8, 'big'), encode_sig(r, s),
                                         private_key.get_public_key()):
                            print('Verified private key by using the corresponding public key and verified the signature')
                            print(f'Private key: {private_key}')
                        else:
                            print('Public key corresponding to private key failed to verify original signature')
                            return None
                    return private_key
                else:
                    if public_key is not None:
                        y = public_key.y
                    else:
                        y = pow(g, x, p)
                    if y != pow(g, x, p):
                        print('[-]Incorrect private key computed!!!')
                    private_key = DSA.construct((y, g, p, group_order, x))
                print(f'Private key: {private_key}')
                return private_key
            collected_signatures[signature['r']] = signature
            t.set_description(f'Collected {len(collected_signatures)} signatures')
