from gmpy2 import mpz,floor,gcd,mul, mpq, qdiv, iroot


def fraction_from_qarray(qarray):
    ns = []
    ds = []
    if len(qarray) > 0:
        ns.append(mpz(qarray[0]))
        ds.append(mpz(1))
    if len(qarray) > 1:
        ns.append(mpz(qarray[0]*qarray[1]+1))
        ds.append(mpz(qarray[1]))
    for i, q in enumerate(qarray[2:],2):
        ns.append(mpz(q*ns[i-1] + ns[i-2]))
        ds.append(mpz(q*ds[i-1] + ds[i-2]))
        if ns[i]*ds[i-1]-ns[i-1]*ds[i] != (-1)**(i+1):
            print('Something weird happened in fraction reconstruction at i={0}'.format(i))
    return mpq(ns[-1],ds[-1])

def continued_fraction_expansion(numerator,denominator):
    f = mpq(numerator,denominator)
    q = [mpz(mpq(numerator,denominator))]
    r = [f-q[0]]
    while r[-1] != 0:
        q.append(mpz(mpq(1,r[-1])))
        r.append(mpq(1,r[-1])-q[-1])
        if 1/(r[-1]+q[-1]) != r[-2]:
            print('Something weird happened when computing continued_fraction_expansion')
    return q

def continued_fraction_extension(qarray=[], rarray=[],numerator=0,denominator=1):
    try:
        f = qdiv(1,rarray[-1])
    except IndexError:
        f = qdiv(numerator,denominator)
    qarray.append(mpz(f))
    rarray.append(f-qarray[-1])

def fraction_extensions(qarray, ns=[],ds=[]):
    if len(qarray) == 1:
        ns.append(qarray[0])
        ds.append(1)
    elif len(qarray) == 2:
        ns.append(ns[-1]*qarray[1]+1)
        ds.append(qarray[1])
    else:
        ns.append(qarray[-1]*ns[-1]+ns[-2])
        ds.append(qarray[-1]*ds[-1]+ds[-2])

def wiener_attack(e,N):
    issquare = True
    qarray = []
    r = []
    continued_fraction_extension(qarray=qarray,rarray=r,numerator=e,denominator=N)
    ns = []
    ds = []
    while r[-1] != 0:
        fraction_extensions(qarray,ns=ns,ds=ds)
        k, dg = ns[-1], ds[-1]
        if len(ns) % 2 == 1:
            k += ns[len(ns)-1] if len(ns)>1 else 1
            dg += ds[len(ds)-1] if len(ns)>1 else 0
        try:
            guessedg = e*dg
        except ValueError as ex:
            print('ValueError at iteration {0}'.format(len(ns)))
            print(ex)
        try:
            guessphin = mpz(qdiv(guessedg,k))
        except ZeroDivisionError:
            print('k=0 when len(ns)={0}'.format(len(ns)))
        guessg = guessedg % k
        guessavgofprimes = qdiv(N-guessphin+1,2)
        if not isinstance(guessavgofprimes,mpz().__class__):
            continued_fraction_extension(qarray=qarray,rarray=r)
            assert qdiv(1,(r[-1]+qarray[-1])) == r[-2], 'Something weird happened when computing continued_fraction_expansion'
            continue
        try:
            guessmidprime, issquare = iroot(guessavgofprimes**2 - N,2)
        except ValueError as myexception:
            print('ValueError in iteration {0}'.format(len(ns)))
            print('Got the following Value Error:{0}'.format(myexception))
        if not issquare:
            continued_fraction_extension(qarray=qarray,rarray=r)
            assert 1/(r[-1]+qarray[-1]) == r[-2], 'Something weird happened when computing continued_fraction_expansion'
            assert guessmidprime**2 != guessavgofprimes**2-N,'Something strange happened'
            continue
        return int(guessavgofprimes - guessmidprime), int(guessavgofprimes + guessmidprime),int(qdiv(dg,guessg))
    print('Wiener attack failed!')

