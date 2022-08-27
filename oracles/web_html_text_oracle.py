from oracles.abstract_oracle import *
from json import loads
import base64
import requests
from bs4 import BeautifulSoup

class WebHTMLTextOracle(AbstractOracle):
    name = 'web_html_text_oracle'

    description = 'Creates an oracle to extract messages from HTML'

    arguments = [OracleArgumentDescription('url','Base URL', True),
                 OracleArgumentDescription('verb', 'HTTP Method for the request', False, defaultValue='GET'),
                 OracleArgumentDescription('inputparam', 'Parameter where input goes if necessary', False, defaultValue=None),
                 OracleArgumentDescription('params', 'Other parameters to add to the request', False, defaultValue='{}'),
                 OracleArgumentDescription('id', 'ID of tag if applicable', False, defaultValue=None),
                 OracleArgumentDescription('tagtype', 'Name of the tag type to look for', False, defaultValue=None),
                 OracleArgumentDescription('valueinattr', 'Name of attribute text we want is in. If not set, default to text', False, defaultValue=None)
            ]

    def makeoracle(self):
        url = self.get_argument_value('url')
        verb = self.get_argument_value('verb')
        inputparam = self.get_argument_value('inputparam')
        paramstring = self.get_argument_value('params')
        params = loads(paramstring)
        id = self.get_argument_value('id')
        tagtype = self.get_argument_value('tagtype')
        valueinattr = self.get_argument_value('valueinattr')
        def oracle(input=None):
            if inputparam:
                if isinstance(input,int):
                    input = f'{input:0{input.bit_length()//4}X}'
                params[inputparam] = input
            resp = requests.request(verb, url,params=params)
            soup = BeautifulSoup(resp.text, 'html.parser')
            if id:
                tag = soup.find(id=id)
                if valueinattr:
                    return tag[valueinattr]
                else:
                    return tag.text
            elif tagtype:
                tags = soup.find_all(tagtype)
                if valueinattr:
                    for tag in tags:
                        try:
                            text = tag[valueinattr]
                            test = base64.b16decode(text.strip())
                        except (KeyError, base64.binascii.Error) as error:
                            continue
                        return text
                else:
                    for tag in tags:
                        text = tag.text
                        try:
                            test = base64.b16decode(text.strip())
                        except base64.binascii.Error:
                            continue
                        return text

        return oracle