
def repeated_nonce(h1,s1,r,h2,s2,q):
    return (((s2*h1-s1*h2)%q)*pow((r*(s1-s2))%q,-1,q))%q