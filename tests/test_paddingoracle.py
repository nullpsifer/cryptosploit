import os
from time import sleep
from icecream import ic
from unittest import TestCase
from base64 import b16decode, b16encode, b64decode
from utils.paddingoracle import PaddingOracleAttack
from random import SystemRandom
from os import urandom
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class TestCipher():

    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: bytes):
        iv = os.urandom(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        padded_plaintext = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        return (b16encode(iv) + b16encode(ciphertext)).decode('utf-8')

    def decrypt(self, ciphertext: str):
        iv = b16decode(ciphertext[:AES.block_size * 2])
        ctext = b16decode(ciphertext[AES.block_size * 2:])
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        padded_plaintext = cipher.decrypt(ctext)
        return unpad(padded_plaintext,AES.block_size,style='pkcs7')


def makeoracle(testcipher: TestCipher):
    def oracle(ciphertext: str):
        try:
            plaintext =testcipher.decrypt(ciphertext)
            return True
        except ValueError as e:
            return False

    return oracle


class TestPaddingOracleAttack(TestCase):
    def test_runattack(self):
        with open('cbc_padding_oracle_texts.txt') as f:
            texts = [b64decode(line.strip().encode('utf-8')) for line in f]
        key = urandom(AES.key_size[-1])
        testcipher = TestCipher(key)
        oracle = makeoracle(testcipher)
        plaintext = SystemRandom().choice(texts)
        ciphertext = testcipher.encrypt(plaintext)
        poa = PaddingOracleAttack(ciphertext, oracle)
        assert plaintext.decode('utf-8') == poa.runattack()
