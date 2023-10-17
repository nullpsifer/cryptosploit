from oracles.abstract_oracle import *
from json import dumps,loads
from ecdsa.ecdsa import Public_key, Private_key, Signature, generator_192
from hashlib import sha1
import socket


class Prosign3(AbstractOracle):
    name = 'prosign3'

    description = 'Creates an oracle to get a signature for cryptohack challenge'

    arguments = [OracleArgumentDescription('socketID', 'Socket ID', True),
            ]

    def makeoracle(self):
        socketID = int(self.get_argument_value('socketID'))
        s = self.sockets[socketID]
        def oracle():
            print(s.recv(1024))
            get_signature = {'option':'sign_time'}
            s.sendall(dumps(get_signature))
            signed_time = loads(s.recv(1024))
            kmax = int(signed_time['msg'].split()[-1].split(':')[-1])
            temp_secret =1221334
            temp_publickey = Public_key(generator_192,generator_192*temp_secret)
            temp_privatekey = Private_key(temp_publickey,temp_secret)
            test_msg = b'This is a test message'
            test_hash = sha1(test_msg).digest()
            for k in range(1,kmax):
                test_sig = temp_privatekey.sign(test_hash,k)
                if test_sig.r == int(signed_time['r'],16):
                    break
            signed_time['h'] = int.from_bytes(sha1(signed_time['msg']).digest(),'big')
            signed_time['k'] = k
            return signed_time

        return oracle