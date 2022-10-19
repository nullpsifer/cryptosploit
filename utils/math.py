from gmpy2 import gcd
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