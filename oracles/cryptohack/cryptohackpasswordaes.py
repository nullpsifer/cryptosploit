from oracles.abstract_oracle import *
from base64 import b16decode
import requests

class CryptohackPasswordAESOracle(AbstractOracle):

    name = 'cryptohack_password_aes'

    description = 'Oracle for completing password AES'

    arguments = []

    def makeoracle(self):
        def oracle(ciphertext, digest):
            url = f'http://aes.cryptohack.org/passwords_as_keys/decrypt/{ciphertext}/{digest}'
            resp = requests.request('get', url,)
            ciphertextjson = resp.json()
            return b16decode(ciphertextjson['plaintext'].upper())
        return oracle
