from oracles.abstract_oracle import *
from json import dumps,loads
from ecdsa.ecdsa import Public_key, Private_key, Signature, generator_192
from hashlib import sha1


class Prosign3(AbstractOracle):
    name = 'prosign3'

    description = 'Creates an oracle to get a signature for cryptohack challenge'

    arguments = [OracleArgumentDescription('socketID', 'Socket ID', True),
            ]

    def makeoracle(self):
        socketID = self.get_argument_value('socketID')
        s = self.sockets[int(socketID)][-1]
        def oracle():
            print(s.recv(1024))
            get_signature = {'option':'sign_time'}
            s.sendall(dumps(get_signature).encode('utf-8'))
            signed_time = loads(s.recv(1024))
            kmax = int(signed_time['msg'].split()[-1].split(':')[-1])
            print(f'{kmax=}')
            temp_secret = 123124
            temp_publickey = Public_key(generator_192, generator_192*temp_secret)
            temp_privatekey = Private_key(temp_publickey, temp_secret)
            temp_msg = b'This is a test'
            temp_hash = int.from_bytes(sha1(temp_msg).digest(),'big')
            for k in range(1,kmax):
                temp_sig = temp_privatekey.sign(temp_hash,k)
                if temp_sig.r == int(signed_time['r'],16):
                    break
            print(f'{k=}')
            signed_time['h'] = int.from_bytes(sha1(signed_time['msg'].encode('utf-8')).digest(),'big')
            signed_time['k'] = k
            signed_time['r'] = int(signed_time['r'],16)
            signed_time['s'] = int(signed_time['s'],16)

            return signed_time

        return oracle