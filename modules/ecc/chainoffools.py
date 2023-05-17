from modules.abstract_module import *
from utils.eccert import chainoffools
from ecpy.curves import Curve, Point
from cryptography.x509 import Certificate

class ChainOfFools(AbstractModule):
    name = 'chainoffools'

    description = 'Creates Private Keys and new generators to match ECC public keys'

    arguments = [ModuleArgumentDescription('public_keys', 'Set of elliptic curve public keys or certificates', required=True),
                 ModuleArgumentDescription('which_keys', 'Potentially comma separated list of indices for choice of keys', required=False, defaultValue='')
                 ]
                 
    oracle = None
    oracleRequired = False

    def _processkey(self,public_key):
        if isinstance(public_key,dict):
            curve = Curve.get_curve(public_key['name'])
            return Point(*public_key['public_key'], curve)
        if isinstance(public_key,Certificate):
            curve = Curve.get_curve(public_key.public_key().curve.name)
            return Point(public_key.public_key().public_numbers().x,
                         public_key.public_key().public_numbers().y,
                         curve)

    def execute(self):
        public_keys = self.get_argument_value('public_keys')
        try:
            which_keys = [int(x) for x in self.get_argument_value('which_keys').split(',') if x != '']
        except ValueError:
            which_keys = [x for x in self.get_argument_value('which_keys').split(',') if x != '']
        if isinstance(public_keys, dict):
            if len(which_keys) > 0:
                keys = which_keys
            else:
                keys = public_keys.keys()
            private_keys = dict()
            for key in keys:
                private_keys[key] = chainoffools(self._processkey(public_keys[key]))
        else:
            if len(which_keys) > 0:
                private_keys = [chainoffools(self._processkey(public_keys[i])) for i in which_keys]
            else:
                private_keys = [chainoffools(self._processkey(key)) for key in public_keys]
            if len(private_keys) == 1:
                private_keys = private_keys[0]
        return private_keys
