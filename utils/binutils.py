import base64
import string

hexdigits = set(string.hexdigits)

def hex2base64(hexstring):
    return base64.b64encode(base64.b16decode(hexstring.upper())).decode('utf-8')

def base642hex(b64string):
    return base64.b16encode(base64.b64decode(b64string)).decode('utf-8')

def xorhexstrings(hexstring1,hexstring2):
    assert len(hexstring1) == len(hexstring2) and len(hexstring2) % 2 == 0
    return f'{int(hexstring1,16)^int(hexstring2,16):0{len(hexstring2)}X}'

def makerepeatedkey(key,textlength):
    newkey = textlength//len(key) * key
    newkey += key[:textlength%len(key)]
    return newkey

def hexifystring(cls,mystring):
    if set(mystring.upper()) < cls.hexdigits:
        return mystring.upper()
    return base64.b16encode(mystring.encode('utf-8')).decode('utf-8')

def hammingdistance(cls,string1,string2):
    mystring1,mystring2 = cls.hexifystring(string1), cls.hexifystring(string2)
    assert len(mystring1) == len(mystring2)
    xorstring = cls.xorhexstrings(mystring1,mystring2)
    distance = 0
    xorint = int(xorstring,16)
    for i in range(4*len(xorstring)):
        if xorint & 1 << i:
            distance += 1
    return distance

def makeblocks(hexstring,blocksize,mustbedivisible=False):
    if mustbedivisible:
        assert len(hexstring)%(2*blocksize) == 0
    blocks = []
    hexlength = len(hexstring)
    for i in range(0,hexlength,2*blocksize):
        if i+2*blocksize>hexlength:
            break
        blocks.append(hexstring[i:i+2*blocksize])
    return blocks

class FileHelper():

    @staticmethod
    def readb64filetohex(filename):
        with open(filename) as f:
            return BinUtils.base642hex(''.join(f.read().split()))
    @staticmethod
    def readb64filetobytes(filename):
        with open(filename) as f:
            return base64.b64decode(''.join(f.read().split()))