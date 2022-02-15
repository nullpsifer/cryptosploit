class PKCS7Exception(Exception):
    def __str__(self):
        return 'Invalid Pad'

class PKCS7:

    def __init__(self, blocksize: int = 16):
        self.blocksize = blocksize

    def pad(self, bytestring: bytes):
        padsize = self.blocksize - (len(bytestring)%16)
        return bytestring + padsize.to_bytes(1,'little')*padsize

    def unpad(self, bytestring: bytes):
        lastbyte = bytestring[-1]
        if 0 < lastbyte <= self.blocksize and bytestring[-lastbyte:] == lastbyte.to_bytes(1,'big')*lastbyte:
            return bytestring[:-lastbyte]
        raise PKCS7Exception