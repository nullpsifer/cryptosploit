import hashlib
from gmpy2 import iroot
from os import urandom

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
def bleichenbacher06(bitsize :int,message :str,hashfunction :str):
    bytesize = bitsize >> 3
    header = b'\x00\x01\xff\x00' + HASH_ASN1[hashfunction]
    beforejunk = header + hashlib.__dict__[hashfunction](message.encode('utf-8')).digest()
    includingjunk = beforejunk + urandom(bytesize-len(beforejunk))
    intval = int.from_bytes(includingjunk,'big')
    s = iroot(intval,3)
    return int(s[0])


