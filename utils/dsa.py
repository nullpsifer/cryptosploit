from hashlib import sha256
def DSASign(privkey,k,m, hashalg):
    g = privkey['g']
    p = privkey['p']
    q = privkey['q']
    x = privkey['x']
    r=pow(g,k,p)%q
    if r==0:
        return 0
    else:
        h = int.from_bytes(hashalg(m).digest(),'big')
        print(h)
        s=(pow(k,-1,q)*(h+x*r))%q
        if s==0:
            return 0
        else:
            return {'r':r,
                          's':s,
                          'm':m.decode('utf-8'),
                          'hashAlgo':'sha256'}

def DSAVerify(pubkey,sig):
    p = pubkey['p']
    q = pubkey['q']
    g = pubkey['g']
    y = pubkey['y']
    r=sig['r']
    s=sig['s']
    m=sig['m']
    w=pow(s,-1,q)
    u1=(int(sha256(m.encode('utf-8')).hexdigest(),16)*w)%q
    u2=r*w%q
    v=((pow(g,u1,p)*pow(y,u2,p))%p)%q
    return v==(r%q)

def repeated_nonce(h1,s1,r,h2,s2,q):
    return (((s2*h1-s1*h2)%q)*pow((r*(s1-s2))%q,-1,q))%q