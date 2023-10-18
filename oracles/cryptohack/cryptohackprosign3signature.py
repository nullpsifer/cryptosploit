from oracles.abstract_oracle import *
from json import dumps,loads
from base64 import b16decode
from ecpy.formatters import decode_sig
from hashlib import sha1


class Prosign3Signature(AbstractOracle):
    name = 'prosign3signature'

    description = 'Creates an oracle to send a signature for cryptohack challenge'

    arguments = [OracleArgumentDescription('socketID', 'Socket ID', True),
            ]

    def makeoracle(self):
        socketID = self.get_argument_value('socketID')
        sock = self.sockets[int(socketID)][-1]
        def oracle(signature :dict):
            new_signature = {'option':'sign_time'}
            new_signature['msg'] = signature['m']
            sig = b16decode(signature['signature'].encode('utf-8'))
            r,s = decode_sig(sig)
            new_signature['r'] = f'{r:0{r.bit_length()//4}x}'
            new_signature['s'] = f'{s:0{s.bit_length()//4}x}'
            sock.sendall(dumps(new_signature).encode('utf-8'))
            raw_resp = sock.recv(1024)
            resp = loads(raw_resp)
            return resp['flag']

        return oracle