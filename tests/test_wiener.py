from Crypto.PublicKey import RSA
from unittest import TestCase
from utils.wiener import wiener_attack
from gmpy2 import lcm
import os


class Test_Wiener(TestCase):
    def test_wiener_attack(self):
        while True:
            d = int.from_bytes(os.urandom(128),'big')
            if d.bit_length() >= 1024:
                continue
            key = RSA.generate(4096)
            phi = (key.p-1)*(key.q-1)
            try:
                e = pow(d,-1,phi)
                break
            except:
                continue
        print(f'{key.n=}\n{e=}')
        try:
            p,q,d = wiener_attack(e,key.n)
        except:
            assert False
        print(f'Successfully returned {p=}\n{q=}{d=}')
        assert (key.p, key.q, d) == (p,q,d)
