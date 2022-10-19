from tqdm import tqdm
from utils.binutils import *
from utils.pkcs7 import PKCS7

class PaddingOracleAttack:

    def __init__(self, ciphertext: str, oracle: callable, blocksize=16):
        self.blocksize = blocksize
        self.ctextblocks = makeblocks(ciphertext.encode('utf-8'), self.blocksize)
        self.oracle = oracle
        self.paddingsize = 1
        self.numberofctextblocks = len(self.ctextblocks) - 1
        self.tqdm = tqdm(total=16 * self.numberofctextblocks)
        self.currentblock = self.numberofctextblocks
        self.plaintext = bytearray(b'')
        self.pad = 1
        self.currentblockint = int(self.ctextblocks[self.currentblock - 1], 16)
        self.keepgoing = True
        self.beginning = True

    def makepad(self):
        self.pad = 0
        for i in range(self.paddingsize):
            self.pad |= self.paddingsize << (8 * i)

    def increment_pad(self):
        self.paddingsize += 1
        if self.paddingsize > self.blocksize:
            self.paddingsize = 1
            self.currentblock -= 1
            self.plaintext = self.guess + self.plaintext
            self.initialize_guess()
            self.currentblockint = int(self.ctextblocks[self.currentblock - 1], 16)
            if self.currentblock == 0:
                self.keepgoing = False
        self.makepad()

    def initialize_guess(self):
        self.guess = bytearray((b'\x00' * (self.blocksize - 1)) + (b'\x10' if self.beginning else b'\x20'))

    def print_currentguess(self):
        currentplaintext = b'0' * (2 * self.blocksize * (self.currentblock - 1)) + base64.b16encode(
            self.guess) + base64.b16encode(self.plaintext)
        self.tqdm.set_description(f'Current guess: {currentplaintext.decode("utf-8")}')

    def update_guess(self):
        if self.beginning:
            self.guess[-self.paddingsize] = (self.guess[-self.paddingsize] - 1) % 256
        else:
            self.guess[-self.paddingsize] = (self.guess[-self.paddingsize] + 1) % 256

    def replaceblock(self):
        self.replacementblock = f'{int.from_bytes(self.guess, "big") ^ self.pad ^ self.currentblockint:0{2 * self.blocksize}X}'.encode(
            'utf-8')

    def makeciphertext(self):
        return b''.join(
            self.ctextblocks[:self.currentblock - 1] + [self.replacementblock, self.ctextblocks[self.currentblock]])

    def step(self):
        self.replaceblock()
        ciphertext = self.makeciphertext()
        self.print_currentguess()
        if self.oracle(ciphertext):
            if self.beginning:
                self.paddingsize = self.guess[-1]
                self.guess = bytearray(b'\x00' * (self.blocksize - self.paddingsize) + self.guess[-1].to_bytes(1,
                                                                                                               'big') * self.paddingsize)
                self.beginning = False
                self.tqdm.update(n=self.paddingsize)
            else:
                self.tqdm.update(n=1)
            self.increment_pad()
        self.update_guess()

    def runattack(self):
        self.initialize_guess()
        while self.keepgoing:
            # self.print_currentguess()
            self.step()
        pad = PKCS7()
        return pad.unpad(self.plaintext).decode('utf-8')
