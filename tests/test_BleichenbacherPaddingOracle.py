from unittest import TestCase
from utils.BleichenbacherPaddingOracle import BleichenbacherPOA
from utils.pkcs15 import PKCS15, PKCS15Exception
from Crypto.PublicKey import RSA


class TestBleichenbacherPOA(TestCase):
    def test_run(self):
        key = RSA.generate(1024)
        pkcs15 = PKCS15(key.n.bit_length()//8)
        message = b'Homomorphisms and bad padding are a dangerous combination'
        paddedmessage = pkcs15.pad(message)
        m = paddedmessage
        #print(f'{m:0{key.n.bit_length()//4}x}')
        c = pow(m,key.e,key.n)
        def makeoracle(key):
            def oracle(c):
                try:
                    m = pkcs15.unpad(pow(c,key.d,key.n))
                except PKCS15Exception:
                    return False
                return True
            return oracle
        oracle = makeoracle(key)
        bleichenbacker = BleichenbacherPOA(key.n,key.e,c,oracle)
        decryptedmessage = bleichenbacker.run()
        print(f'Found: {decryptedmessage}')
        assert message == decryptedmessage
