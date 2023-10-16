from oracles.abstract_oracle import *
from json import dumps,loads
from ecdsa.ecdsa import Public_key, Private_key, Signature, generator_192
import socket


class Prosign3(AbstractOracle):
    name = 'prosign3'

    description = 'Creates an oracle to get a signature for cryptohack challenge'

    arguments = [OracleArgumentDescription('socketID', 'Socket ID', True),
            ]

    def makeoracle(self):
        port = self.terminalself.get_argument_value('socketID')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,int(port)))
        def oracle():
            print(s.recv(1024))
            get_signature = {'option':'sign_time'}
            s.sendall(dumps(get_signature))
            signed_time = loads(s.recv(1024))
            
            return databack

        return oracle