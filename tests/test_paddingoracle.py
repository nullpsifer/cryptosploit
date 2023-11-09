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

plaintexts = ["MDAwMDAwTm93IHRoYXQgdGhlIHBhcnR5IGlzIGp1bXBpbmc=",
            "MDAwMDAxV2l0aCB0aGUgYmFzcyBraWNrZWQgaW4gYW5kIHRoZSBWZWdhJ3MgYXJlIHB1bXBpbic=",
            "MDAwMDAyUXVpY2sgdG8gdGhlIHBvaW50LCB0byB0aGUgcG9pbnQsIG5vIGZha2luZw==",
            "MDAwMDAzQ29va2luZyBNQydzIGxpa2UgYSBwb3VuZCBvZiBiYWNvbg==",
            "MDAwMDA0QnVybmluZyAnZW0sIGlmIHlvdSBhaW4ndCBxdWljayBhbmQgbmltYmxl",
            "MDAwMDA1SSBnbyBjcmF6eSB3aGVuIEkgaGVhciBhIGN5bWJhbA==",
            "MDAwMDA2QW5kIGEgaGlnaCBoYXQgd2l0aCBhIHNvdXBlZCB1cCB0ZW1wbw==",
            "MDAwMDA3SSdtIG9uIGEgcm9sbCwgaXQncyB0aW1lIHRvIGdvIHNvbG8=",
            "MDAwMDA4b2xsaW4nIGluIG15IGZpdmUgcG9pbnQgb2g=",
            "MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93"]

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
        texts = [b64decode(line.strip().encode('utf-8')) for line in plaintexts]
        key = urandom(AES.key_size[-1])
        testcipher = TestCipher(key)
        oracle = makeoracle(testcipher)
        plaintext = SystemRandom().choice(texts)
        ciphertext = testcipher.encrypt(plaintext)
        poa = PaddingOracleAttack(ciphertext, oracle)
        assert plaintext.decode('utf-8') == poa.runattack()
