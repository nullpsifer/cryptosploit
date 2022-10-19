from tqdm import trange, tqdm
from utils import binutils
import base64
import string

def isECB(ciphertext: str, blocksize: int=16):
    print(f'Checking {ciphertext=} with {blocksize=}')
    blocks = binutils.makeblocks(ciphertext, blocksize)
    return len(set(blocks)) < len(blocks)

class NotECBModeException(Exception):

    pass


class ByteAtATimeDecryptionECB:

    def __init__(self, oracle):
        # Trying to order bytes to minimize iterations
        initialBytes = (
                    'etaoinshrdlcumwfgypbvkjxqz' + 'etaoinshrdlcumwfgypbvkjxqz'.upper() + string.digits + string.whitespace + string.punctuation).encode(
            'utf-8')
        self.testbytes = initialBytes + b''.join(
            [i.to_bytes(1, 'little') for i in range(256) if i not in set(initialBytes)])
        self.oracle = oracle
        self.blocksize = 0
        self.textlength = 0

    def detect_blocklength(self):
        print('[+] Checking for ECB Mode')
        print('[+] Checking to see if there is a minimal input needed')
        teststr = b''
        necessaryinput = 0
        while True:
            currentlength = len(self.oracle(teststr))
            if currentlength == 0:
                teststr += b'A'
                necessaryinput += 1
            else:
                break
        print(f'[+] Found minimal input length = {necessaryinput}')
        self.textlength = (currentlength // 2)- necessaryinput
        print('[+] Looking for minimal input to get an additional block')
        while True:
            teststr += b'A'
            ciphertext = self.oracle(teststr)
            print(ciphertext)
            if currentlength < len(ciphertext):
                currentlength = len(ciphertext)
                break
        print('[+] Found input to get new block')
        while True:
            teststr += b'A'
            newciphertext = self.oracle(teststr)
            if currentlength < len(newciphertext):
                self.blocksize = (len(newciphertext)-currentlength)//2
                return self.blocksize

    def detect_ECB(self):
        return isECB(self.oracle(b'A' * (4 * self.blocksize)))

    def crack(self):
        test = b'A' * (self.blocksize - 1)
        self.plaintext = b''
        bufferblock = b'A' * (self.blocksize - 1)
        t = trange(self.textlength)
        for i in t:
            for j in range(256):
                texttoprint = ''
                for k in range(len(self.plaintext)):
                    try:
                        texttoprint += self.plaintext[k:k + 1].decode('utf-8')
                    except:
                        texttoprint += base64.b16encode(self.plaintext[k:k + 1]).decode('utf-8')
                try:
                    texttoprint += self.testbytes[j:j + 1].decode('utf-8')
                except:
                    texttoprint += base64.b16encode(self.testbytes[j:j + 1]).decode('utf-8')

                texttoprint = texttoprint.replace('\n', '\\n')
                t.set_description(f'plaintext = {texttoprint}')
                ciphertext = self.oracle(test + self.testbytes[j:j + 1] + bufferblock)
                ciphertextblcoks = binutils.makeblocks(ciphertext, self.blocksize)
                if ciphertextblcoks[0] in ciphertextblcoks[1:]:
                    self.plaintext += self.testbytes[j:j + 1]
                    break
            test = test[1:] + self.plaintext[len(self.plaintext) - 1:len(self.plaintext)]
            if len(bufferblock) == 0:
                bufferblock = b'A' * (self.blocksize)
            bufferblock = bufferblock[1:]
        pkcs7 = PKCS7(self.blocksize)
        self.plaintext = pkcs7.unpad(self.plaintext)
        return self.plaintext.decode('utf-8')

    def run(self):
        print('[+] Determining blocksize')
        self.detect_blocklength()
        print(f'[+] Found blocksize {self.blocksize}')
        print('[+] Checking for ECB Mode')
        if self.detect_ECB():
            print('[+] ECB Mode detected')
            return self.crack()
        print('[-] Does not appear to be ECB Mode')
        raise NotECBModeException

