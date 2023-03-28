from gmpy2 import gcd
from utils.units import GroupOfUnits
from math import ceil, sqrt
from primefac import factorint
class InverseException(Exception):

    def __init__(self,divisor,modulus):
        self.divisor = divisor
        self.modulus = modulus

    def __str__(self):
        return f'InverseException: common divisor {self.divisor} found with modulus {self.modulus}'

def sunzi(congruences):
    congruences.sort(key=lambda x:x[1])
    a,n = congruences.pop()
    while len(congruences) > 0:
        ai,ni=congruences.pop()
        ninverse = inverse(n,ni)
        x=((ai-a)*ninverse)%ni
        a += x*n
        n *= ni
    return a,n

def inverse(x,n):
    try:
        return pow(x,-1,n)
    except ValueError:
        raise InverseException(gcd(x,n), n)

def legendresymbol(a,p):
    return pow(a,(p-1)//2,p)

def modular_sqrt(n,p):
    if p%4==3:
        x = pow(n,(p+1)//4,p)
        return [x,p-x]
    else:
        q,s = p-1,0
        print('Entering first loop')
        while q%2 == 0:
            q //=2
            s += 1
        z = 2
        print('Entering second loop')
        ls = legendresymbol(z,p)
        while ls != p-1:
            z += 1
            ls = legendresymbol(z,p)
        m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
        print('Entering third loop')
        while t != 1:
            pow_t = pow(t, 2, p)
            print('Entering inner loop')
            for j in range(1, m):
                if pow_t == 1:
                    m_update = j
                    break
                pow_t = pow(pow_t, 2, p)
            b = pow(c, int(pow(2, m - m_update - 1)), p)
            m, c, t, r = m_update, pow(b, 2, p), t * pow(b, 2, p) % p, r * b % p
        #check_sqrt(r, n, p)
        return [r, p - r]

def babystep_giantstep(g,h,p):
    m = ceil(sqrt(p))
    mytable = {g.zaction(j)._g: j for j in range(m)}
    try:
        gminv = g.zaction(-m)
    except ValueError:
        return 0
    for i in range(m):
        try:
            return mytable[h.operation(gminv.zaction(i))._g] + i*m
        except KeyError:
            continue
    print('Failed')
    print(mytable)
    return None

def naivedlog(g,h,n):
    x = g
    print(x)
    for i in range(n+1):
        if x.zaction(i) == h:
            return i
    print(f'Failed to find discrete log\n{h=}\n{x=}\n{n=}')

def primepower(g, h, p, e):
    x = 0
    if pow(p,e) < 1000:
        return naivedlog(g,h,pow(p,e))
    gamma = g.zaction(pow(p,e-1))
    hk = []
    for k in range(e):
        hk.append(g.zaction(-x).operation(h).zaction(pow(p,e-1-k)))
        if p < 10000:
            d = naivedlog(gamma, hk[-1],p)
        else:
            d = babystep_giantstep(gamma,hk[-1],p)
        x += pow(p,k)*d
    return x

def pohlig_hellman(g,h,p):
    g= GroupOfUnits(g,p)
    h = GroupOfUnits(h,p)
    order = p-1
    order_factors = factorint(order)
    congruences = []
    for pk,ek in order_factors.items():
        gk = g.zaction(order//pow(pk,ek))
        hk = h.zaction(order//pow(pk,ek))
        print(f'{gk=}\n{hk=}')
        if gk.is_identity():
            print(f'{g} has order divisible of {pow(pk,ek)}')
            continue
        congruences.append((primepower(gk, hk, pk, ek),pow(pk,ek)))
    return sunzi(congruences)[0]
