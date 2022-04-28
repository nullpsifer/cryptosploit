from oracles.abstract_oracle import *
from json import loads
import requests

class WebStatusBinaryOracle(AbstractOracle):
    name = 'web_status_binary_oracle'

    description = 'Creates a binary oracle based on HTTP status code'

    arguments = [OracleArgumentDescription('url','Base URL', True),
                 OracleArgumentDescription('verb', 'HTTP Method for the request', False, defaultValue='GET'),
                 OracleArgumentDescription('cipherparam', 'Parameter that contains the ciphertext', True),
                 OracleArgumentDescription('params', 'Other parameters to add to the request', False, defaultValue='{}'),
                 OracleArgumentDescription('goodstatuses', 'Comma separated list of good status codes', True),

    def makeoracle(self):
        url = self.get_argument_value('url')
        verb = self.get_argument_value('verb')
        cipherparam = self.get_argument_value('cipherparam')
        paramstring = self.get_argument_value('params')
        params = loads(paramstring)
        goodstatuses = set(map(int,split(',',self.get_argument_value('goodstatuses'))))
        def oracle(ctext):
            params[cipherparam] = ctext
            if verb == 'GET':
                resp = requests.get(url,params=params)
            else:
                resp = requests.post(url,params=params)
            return resp.status_code in goodstatuses

        return oracle