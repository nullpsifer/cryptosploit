from oracles.abstract_oracle import *
from json import loads
import requests

class WebStatusBinaryOracle(AbstractOracle):
    name = 'web_status_boolean_oracle'

    description = 'Creates a binary oracle based on HTTP status code'

    arguments = [OracleArgumentDescription('url','Base URL', True),
                 OracleArgumentDescription('verb', 'HTTP Method for the request', False, defaultValue='GET'),
                 OracleArgumentDescription('cipherparam', 'Parameter that contains the ciphertext', True),
                 OracleArgumentDescription('params', 'Other parameters to add to the request', False, defaultValue='{}'),
                 OracleArgumentDescription('goodstatuses', 'Comma separated list of good status codes', True),
            ]

    def makeoracle(self):
        url = self.get_argument_value('url')
        verb = self.get_argument_value('verb')
        cipherparam = self.get_argument_value('cipherparam')
        paramstring = self.get_argument_value('params')
        params = loads(paramstring)
        goodstatuses = set(map(int,self.get_argument_value('goodstatuses').split(',')))
        #print(goodstatuses)
        def oracle(ctext):
            if isinstance(ctext,int):
                ctext = f'{ctext:0{ctext.bit_length()//4}X}'
            params[cipherparam] = ctext
            if verb == 'GET':
                resp = requests.get(url,params=params)
            else:
                resp = requests.post(url,params=params)
            statuscode = resp.status_code
            #print(f'{statuscode=}')
            return statuscode in goodstatuses

        return oracle