import base64

from oracles.abstract_oracle import *
import requests
from json import loads

class WebPostJsonSignature(AbstractOracle):
    name = 'web_post_json_signature'
    description = 'Oracle that submits signatures'
    arguments = [OracleArgumentDescription('components','A comma separated list of components of the signature', True),
                 OracleArgumentDescription('keys', 'A comma separated list of the keys in the JSON signature corresponding to the components', True),
                 OracleArgumentDescription('url','URL to the end point',True),
                 OracleArgumentDescription('encoding','encoding for bytes values {hex, base64',False, defaultValue='hex'),
                 OracleArgumentDescription('cookies','Any necessary cookies', False, defaultValue='{}'),
                 OracleArgumentDescription('headers', 'Additional headers', False, defaultValue='{}')]

    def makeoracle(self):
        url = self.get_argument_value('url')
        cookies = loads(self.get_argument_value('cookies'))
        headers = loads(self.get_argument_value('headers'))
        encoding = self.get_argument_value('encoding')
        encodingfunctions = {'hex': lambda x: base64.b16encode(x).decode('utf-8'),
                             'base64': lambda x: base64.b64encode(x).decode('utf-8')}
        components = self.get_argument_value('components').split(',')
        keys = self.get_argument_value('keys').split(',')
        def oracle(signature):
            newsignature = {}
            for i,component in enumerate(components):
                newsignature[keys[i]] = signature[component]
                if isinstance(newsignature[keys[i]], bytes):
                    newsignature[keys[i]] = encodingfunctions[encoding](newsignature[keys[i]])
            print(newsignature)
            resp = requests.post(url,json=newsignature,cookies=cookies,headers=headers)
            return resp.json()
        return oracle