import os
import hashlib
class PKCS15Exception(Exception):
    pass

class PKCS15:
    HASH_ASN1 = {
        'md5': b'\x30\x20\x30\x0c\x06\x08\x2a\x86'
               b'\x48\x86\xf7\x0d\x02\x05\x05\x00\x04\x10',
        'sha1': b'\x30\x21\x30\x09\x06\x05\x2b\x0e'
                b'\x03\x02\x1a\x05\x00\x04\x14',
        'sha256': b'\x30\x31\x30\x0d\x06\x09\x60\x86'
                  b'\x48\x01\x65\x03\x04\x02\x01\x05\x00\x04\x20',
        'sha384': b'\x30\x41\x30\x0d\x06\x09\x60\x86'
                  b'\x48\x01\x65\x03\x04\x02\x02\x05\x00\x04\x30',
        'sha512': b'\x30\x51\x30\x0d\x06\x09\x60\x86'
                  b'\x48\x01\x65\x03\x04\x02\x03\x05\x00\x04\x40',
    }
    def __init__(self,bytelength):
        self.bytelength =bytelength

    def pad(self,m :bytes)->int:
        messagelength = len(m)
        if messagelength > self.bytelength -11:
            raise PKCS15Exception
        randombytelength = self.bytelength - 3 - messagelength
        pad = os.urandom(randombytelength)
        while 0 in pad:
            pad = os.urandom(randombytelength)
        return  int.from_bytes(b'\x00\x02'+ pad + b'\x00' + m,'big')

    def unpad(self,m :int)->bytes:
        '''Do not use this implementation in real life. This is designed to be vulnerable to Bleichenbacher
           Padding Oracle attacks, both because of quitting early, and the use of the exception'''
        msg = m.to_bytes(self.bytelength,'big')
        if msg[:2] != b'\x00\x02':
            raise PKCS15Exception
        #print('Found valid start')
        i = msg.find(b'\x00',2)
        msg = msg[i+1:]
        if len(msg) > self.bytelength - 11 or len(msg)==0:
            raise PKCS15Exception
        return msg

    def signaturePad(self,message :bytes,hashalgorithm :str):
        digest = hashlib.__dict__[hashalgorithm](message).digest()
        end = self.HASH_ASN1[hashalgorithm]+digest
        mbytes = b'\x00\x01'+(self.bytelength-3-len(end))*b'\xff'+b'\x00'+end
        return int.from_bytes(mbytes,'big')