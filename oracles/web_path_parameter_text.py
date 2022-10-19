from oracles.abstract_oracle import *
from json import loads
import base64
import requests

class WebHTMLTextOracle(AbstractOracle):
    name = 'web_json_path_text_oracle'

    description = 'Creates an oracle to extract messages from HTML'

    arguments = [OracleArgumentDescription('url','Full URL where the input path component should be specified as {input}', True),
                 OracleArgumentDescription('verb', 'HTTP Method for the request', False, defaultValue='GET'),
                 OracleArgumentDescription('params', 'Other parameters to add to the request', False, defaultValue='{}'),
                 OracleArgumentDescription('encodeInput', 'If input needs to be encoded specify here', False, defaultValue=None),
                 OracleArgumentDescription('jsonkey', 'JSON key with text', True),
            ]

    def makeoracle(self):
        url = self.get_argument_value('url')
        verb = self.get_argument_value('verb')
        paramstring = self.get_argument_value('params')
        jsonkey = self.get_argument_value('jsonkey')
        params = loads(paramstring)
        if self.get_argument_value('encodeInput'):
            encoder = base64.__dict__[self.get_argument_value('encodeInput')]
        else:
            encoder = lambda x: x
        def oracle(input):
            testurl = url.format(input=encoder(input).decode('utf-8'))
            try:
                resp = requests.request(verb, testurl,params=params)
                data = resp.json()
                return data[jsonkey]
            except:
                return ''
        return oracle