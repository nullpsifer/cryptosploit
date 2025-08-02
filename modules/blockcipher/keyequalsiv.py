from modules.abstract_module import *
from utils.ecboracleattack import ByteAtATimeDecryptionECB, NotECBModeException
from base64 import b64decode, b64encode

class ECBOracleModule(AbstractModule):
    name = 'keyequalsiv'

    description = 'Key=IV attack with decryption oracle'

    arguments = [ModuleArgumentDescription('ciphertext','Ciphertext',True),
                 ModuleArgumentDescription('encoding','Encoding: hex, base64, raw',False,defaultValue='hex'),
                 ModuleArgumentDescription('blocksize','Blocksize in bytes of the cipher',False,defaultValue='16')]

    oracle = None
    oracleRequired = True
    decoder = {'hex':lambda x: bytes.fromhex(x),
               'base64': lambda x: b64decode(x),
               'raw': lambda x: x}
    encoder = {'hex': lambda x: x.hex(),
               'base64': lambda x: b64encode(x),
               'raw': lambda x: x}

    def execute(self):
        ciphertext = self.get_argument_value('ciphertext')
        encoding = self.get_argument_value('encoding')
        ciphertextbytes = self.decoder[encoding](ciphertext)
        blocksize = int(self.get_argument_value('blocksize'))
        newciphertext = ciphertextbytes[:blocksize]+blocksize*b'\x00'+ciphertextbytes
        oracle = self.oracle.makeoracle()
        plaintext = oracle(self.encoder[encoding](newciphertext))
        plaintextbytes = self.decoder[encoding](plaintext)
        keyint = int.from_bytes(plaintextbytes[:blocksize],'big')^int.from_bytes(plaintextbytes[2*blocksize:3*blocksize],'big')
        key = keyint.to_bytes(blocksize,'big')
        print(f'[+] Found key: {key.hex()}')
        return key

