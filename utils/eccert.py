import copy
from math import ceil
from random import SystemRandom
from ecpy.curves import Curve, Point
from Crypto.Util.asn1 import DerSequence, DerOctetString, DerBitString, DerObjectId

def make_privatekey(d :int,generator :Point):
    curve = generator.curve
    field_byte_length = ceil(curve.field.bit_length()/8)
    public_key = d*generator
    generator = b'\x04' + generator.x.to_bytes(field_byte_length,'big') + generator.y.to_bytes(field_byte_length,'big')
    public_key = b'\x04' + public_key.x.to_bytes(field_byte_length, 'big') + public_key.y.to_bytes(field_byte_length, 'big')
    field_parameters = DerSequence([DerObjectId("1.2.840.10045.1.1"), curve.field])
    parameters = [DerSequence([1, field_parameters,
                               DerSequence([DerOctetString(curve.a.to_bytes(field_byte_length,'big')),
                                            DerOctetString(curve.b.to_bytes(field_byte_length,'big'))]),
                                            DerOctetString(generator),
                                            curve.order,
                                            1])]
    seq = [1,
           DerOctetString(d.to_bytes(field_byte_length,'big')),
           DerSequence(parameters, implicit=0),
           DerBitString(public_key, explicit=1)]

    return seq

def chainoffools(publickey :Point):
    originalcurve = publickey.curve
    newdomain = copy.copy(originalcurve._domain)
    newdomain['name'] = 'CoF' + newdomain['name']
    P = Point(publickey.x, publickey.y,originalcurve)
    d = SystemRandom().randint(1,publickey.curve.field)
    newgenerator = pow(d,-1,publickey.curve.field) * P
    newdomain['generator'] = (newgenerator.x,newgenerator.y)
    newcurve = originalcurve.__class__(newdomain)
    newpublickey = Point(P.x,P.y,newcurve)
    return d, newpublickey