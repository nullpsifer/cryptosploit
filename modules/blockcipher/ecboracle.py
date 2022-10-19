from modules.abstract_module import *
from utils.ecboracleattack import ByteAtATimeDecryptionECB, NotECBModeException

class ECBOracleModule(AbstractModule):
    name = 'ecboracle'

    description = 'Runs a EBC Oracle Attack'

    arguments = []
                 
    oracle = None
    oracleRequired = True

    def execute(self):

        byteatatime = ByteAtATimeDecryptionECB(self.oracle.makeoracle())
        try:
            plaintext = byteatatime.run()
            print(f'{plaintext=}')
            return plaintext
        except NotECBModeException:
            print('[-] Unable to complete attack. ECB Mode not detected')
            return None