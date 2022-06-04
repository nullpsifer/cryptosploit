from oracles.abstract_oracle import *
import requests
from json import loads

class WebPostJsonSignature(AbstractOracle):
    name = 'web_post_json_signature'
    description = 'Oracle that submits signatures'
    arguments = [OracleArgumentDescription('components','A comma separated list of components of the signature', True),
                 OracleArgumentDescription('keys', 'A comma separated list of the keys in the JSON signature corresponding to the components', True),
                 OracleArgumentDescription('url','URL to the end point',True),
                 OracleArgumentDescription('cookies','Any necessary cookies', False, defaultValue='{}'),
                 OracleArgumentDescription('headers', 'Additional headers', False, defaultValue='{}')]

    def makeoracle(self):
        url = self.get_argument_value('url')
        cookies = loads(self.get_argument_value('cookies'))
        headers = loads(self.get_argument_value('headers'))
        components = self.get_argument_value('components').split(',')
        keys = self.get_argument_value('keys').split(',')
        def oracle(signature):
            newsignature = {}
            for i,component in enumerate(components):
                newsignature[keys[i]] = signature[component]
            resp = requests.post(url,json=newsignature,cookies=cookies,headers=headers)
            return resp.json()
        return oracle