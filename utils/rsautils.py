import os
from gmpy2 import gcd, iroot
from utils.math import sunzi


class BroadcastException(Exception):
    def __init__(self, number, power):
        self.number = number
        self.power = power

    def __str__(self):
        return f'{self.number} is not a perfect {self.power}'

def factor_with_exponents(e,d,n):
    k=e*d-1
    r=k
    i=0
    while r%2 == 0:
        r >>= 1
        i += 1
    counter = 0
    while True:
        counter += 1
        x = int.from_bytes(os.urandom(n.bit_length()//8),'big')
        r = k
        for j in range(i):
            r >>= 1
            s = pow(x,r,n)
            if s == n-1:
                break
            if s != 1:
                p = gcd(s-1,n)
                if p == 1:
                    break
                q = n//p
                return p,q

def broadcast_small_e(messagesandkeys, publicexponent):
    commonexponentlist = [message for message in messagesandkeys if message['e'] == publicexponent]
    assert len(commonexponentlist) >= publicexponent
    commonexponentlist.sort(key=lambda x:x['n'])
    commonexponentlist = commonexponentlist[:publicexponent]
    congruences = [(message['c'],message['n']) for message in commonexponentlist]
    largec, _ = sunzi(congruences)
    m,diditwork = iroot(largec, publicexponent)
    if diditwork:
        return int(m)
    else:
        raise BroadcastException(largec,publicexponent)
