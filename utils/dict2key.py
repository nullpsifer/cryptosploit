from Crypto.PublicKey import RSA, DSA
from ecpy.curves import Point, Curve

def dict2publickey(dictkey :dict):
    try:
        return RSA.construct((dictkey['n'],dictkey['e']))
    except KeyError:
        try:
            return DSA.construct((dictkey['y'],
                                 dictkey['g'],
                                 dictkey['p'],
                                 dictkey['q']))
        except KeyError:
            curve = Curve.get_curve(dictkey['curve'])
            if curve == None:
                raise TypeError
            return Point(dictkey['x'],dictkey['y'],curve)