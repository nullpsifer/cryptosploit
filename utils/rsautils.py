import os
from gmpy2 import gcd

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