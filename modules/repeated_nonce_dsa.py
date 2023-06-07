import utils.dsa as dsa
from tqdm import tqdm
from modules.abstract_module import *
from Crypto.PublicKey import DSA

class RepeatedNonceDSa(AbstractModule):
    name = 'repeated_nonce'

    description = 'This module queries a signature oracle until it gets a repeated r value and then computes the private key'
    arguments = [ModuleArgumentDescription('public_key','Public Signing Key', True)]
    oracle = None
    oracleRequired = True

    def execute(self):
        t = tqdm()
        public_key = self.get_argument_value('public_key')
        p = public_key['p']
        q = public_key['q']
        collected_signatures = dict({})
        oracle = self.oracle.makeoracle()
        print('Collecting Signatures')
        while True:
            signature = oracle()
            print(dsa.DSAVerify(public_key,signature))
            if signature['r'] in collected_signatures.keys():
                r = signature['r']
                s1 = signature['s']
                h1 = signature['h']
                s2 = collected_signatures[signature['r']]['s']
                h2 = collected_signatures[signature['r']]['h']
                x = dsa.repeated_nonce(h1,s1,r,h2,s2,q)
                print(f'Verifying private key: {public_key["y"]==pow(public_key["g"],x,public_key["p"])}')
                print(f'Private key: {x}')
                return DSA.construct((public_key['y'],
                              public_key['g'],
                              public_key['p'],
                              public_key['q'],
                              x))
            collected_signatures[signature['r']] = signature
            t.set_description(f'Collected {len(collected_signatures)} signatures')
