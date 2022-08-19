import os
class PKCS15Exception(Exception):
    pass

class PKCS15:
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