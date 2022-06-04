from oracles.abstract_oracle import *
import hashlib
from json import loads
import requests

class WebJsonSignatureOracle(AbstractOracle):

    name = 'web_json_signature_oracle'

    description = 'Oracle for getting signed messages from HTTP end point'

    arguments = [OracleArgumentDescription('components', 'Comma delimited list of components in a signature',True),
                 OracleArgumentDescription('keys', "The keys used for the necessary components listed in the same order as components", True),
                 OracleArgumentDescription('hashkey','If there is a key for the hash algorithm, set it here',False, defaultValue=None),
                 OracleArgumentDescription('hashalg','If the hash algorithm is not specified, state algorith here', False, defaultValue=''),
                 OracleArgumentDescription('url', 'End point URL', True),
                 OracleArgumentDescription('verb','HTTP verb for the request', False, defaultValue='GET'),
                 OracleArgumentDescription('params', 'Request parameters', False, defaultValue='{}'),
                 OracleArgumentDescription('cookies', 'Request cookies', False, defaultValue=''),
                 OracleArgumentDescription('headers', 'Any special headers needed', False, defaultValue='{}')]

    def makeoracle(self):
        url = self.get_argument_value('url')
        verb = self.get_argument_value('verb')
        components = self.get_argument_value('components').split(',')
        keys = self.get_argument_value('keys').split(',')
        hashkey = self.get_argument_value('hashkey')
        hashalg = self.get_argument_value('hashalg')
        params = self.get_argument_value('params')
        cookies = self.get_argument_value('cookies')
        headers = self.get_argument_value('headers')
        def oracle():
            resp = requests.request(verb, url,params=loads(params),headers=loads(headers),cookies=cookies)
            respsig = resp.json()
            if hashkey:
                hashalg = respsig[hashkey]
            hashfunction = hashlib.__dict__[hashalg]
            signature = {}
            for i, component in enumerate(components):
                signature[component] = respsig[keys[i]]
            signature['h'] = int.from_bytes(hashfunction(signature['m'].encode('utf-8')).digest(),'big')
            return signature
        return oracle

