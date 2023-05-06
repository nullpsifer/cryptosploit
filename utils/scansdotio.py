from base64 import b64decode, b16decode
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_der_x509_certificate
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey
from gzip import GzipFile

def parse_cert(filename, predicate = lambda x: True):
    certs = []
    with GzipFile(filename) as gzfile:
        for line in gzfile:
            certhash, b64der = str(line,encoding='UTF-8').strip().split(',')
            derstring = b64decode(b64der)
            try:
                certs.append(load_der_x509_certificate(derstring,default_backend()))
            except Exception as e:
                print(f'Failed to parse {certhash}, received exception {e}')
    return certs