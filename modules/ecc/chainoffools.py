from modules.abstract_module import *
from utils.eccert import chainoffools
from ecpy.curves import Curve, Point
from cryptography.x509 import Certificate

class ChainOfFools(AbstractModule):
    name = 'chainoffools'

    description = 'Creates Private Keys and new generators to match ECC public keys'

    arguments = [ModuleArgumentDescription('public_keys', 'Set of elliptic curve public keys or certificates', required=True),
                 ModuleArgumentDescription('private_key_format','Data type for the private key, dict or der', required=False, defaultValue='dict')]
                 
    oracle = None
    oracleRequired = False

    def _processkey(self,public_key):
        if isinstance(public_key,dict):
            curve = Curve.get_curve(public_key['curve'])
            return Point(*public_key['public_key'], curve)
        if isinstance(public_key,Certificate):
            curve = Curve.get_curve(public_key.public_key().curve.name)
            return Point(public_key.public_key().public_numbers().x,
                         public_key.public_key().public_numbers().y,
                         curve)

    def execute(self):
        public_keys = self.get_argument_value('public_keys')
        if isinstance(public_keys, dict):
            private_keys = dict()
            for key in public_keys.keys():
                private_keys[key] = chainoffools(self._processkey(public_keys[key]))
        else:
            private_keys = [chainoffools(self._processkey(key)) for key in public_keys]
        return private_keys
