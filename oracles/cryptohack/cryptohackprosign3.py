from oracles.abstract_oracle import *
import socket

class Prosign3(AbstractOracle):
    name = 'prosign3'

    description = 'Creates an oracle to for generic socket connections'

    arguments = [OracleArgumentDescription('host','hostname or IP address', True),
                 OracleArgumentDescription('port', 'TCP port', True),
            ]

    def makeoracle(self):
        host = self.get_argument_value('host')
        port = self.get_argument_value('port')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,int(port)))
        print(s.recv(1024))
        def oracle(input :bytes, done=False):
            s.sendall(input)
            databack = s.recv(1024)
            if done:
                s.close()
            return databack

        return oracle