from oracles.abstract_oracle import *
from json import loads
import requests

class WebJsonPublicKey(AbstractOracle):
    name = 'web_json_public_key'
    description = 'Get a public key from a JSON endpoint'
    arguments = [OracleArgumentDescription('components', 'Comma delimited list of components in a public key',True),
                 OracleArgumentDescription('keys', "The keys used for the necessary components listed in the same order as components", True),
                 OracleArgumentDescription('url', 'End point URL', True),
                 OracleArgumentDescription('verb','HTTP verb for the request', False, defaultValue='GET'),
                 OracleArgumentDescription('params', 'Request parameters', False, defaultValue='{}'),
                 OracleArgumentDescription('cookies', 'Request cookies', False, defaultValue=''),
                 OracleArgumentDescription('headers', 'Any special headers needed', False, defaultValue='{}')]

    def makeoracle(self):
        url = self.get_argument_value('url')
        components = self.get_argument_value('components').split(',')
        keys = self.get_argument_value('keys').split(',')
        verb = self.get_argument_value('verb')
        params = loads(self.get_argument_value('params'))
        cookies = self.get_argument_value('cookies')
        headers = loads(self.get_argument_value('headers'))
        def oracle():
            resp = requests.request(verb, url, params=params,headers=headers,cookies=cookies )
            receivedkey = resp.json()
            if isinstance(receivedkey,list):
                rkeys = []
                for rkey in receivedkey:
                    key ={}
                    for i, component in enumerate(components):
                        key[component] = rkey[keys[i]]
                    rkeys.append(key)
                return rkeys

            key = {}
            for i, component in enumerate(components):
                key[component] = rkey[keys[i]]
            return key
        return oracle
