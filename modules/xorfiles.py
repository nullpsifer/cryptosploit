from modules.abstract_module import *
from sslyze import *

class TlsCipherScanModule(AbstractModule):

    name = "xorfile"

    description = "Scans host for supported TLS cipher suites."

    arguments = [
            ModuleArgumentDescription("file1", "First input file", True),
            ModuleArgumentDescription("file2", "Second input file", True),
            ModuleArgumentDescription("outfile", "output file", True),
    ]
        
    oracle = None
    oracleRequired = False

    def execute(self):
        file1 = self.get_argument_value('file1')
        file2 = self.get_argument_value('file2')
        outfile = self.get_argument_value('outfile')
        with open(file1,'rb') as f:
            in1 = f.read()
        with open(file2,'rb') as f:
            in2 = f.read()
        if len(in1) != len(in2):
            print('File sizes do not match')
            return
        xor=int.from_bytes(in1,'big')^int.from_bytes(in2,'big')
        with open(outfile,'wb') as f:
            f.write(xor.to_bytes(len(in1),'big'))
            print('File written')
            return