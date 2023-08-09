from oracles.abstract_oracle import *
from json import loads
import base64
import requests
from bs4 import BeautifulSoup

class WebJsonGenericPost(AbstractOracle):
    name = 'web_json_generic_post'

    description = 'Generic JSON post'

    arguments = [OracleArgumentDescription('url','Base URL', True),
            ]

    def makeoracle(self):
        url = self.get_argument_value('url')
        def oracle(data):
            resp = requests.post(url=url,json=data)
            data = ''
            try:
                data = resp.json()
            except:
                print(resp.text)
            return data

        return oracle