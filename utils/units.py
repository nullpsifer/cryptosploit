
class GroupOfUnits():

    def __init__(self, g, p):
        self._p = p
        self._g = g

    def __eq__(self, other):
        return self._g == other._g

    def operation(self, otherelement):
        return GroupOfUnits((self._g * otherelement._g)%self._p, self._p)

    def zaction(self, n):
        return GroupOfUnits(pow(self._g,n,self._p),self._p)

    def __repr__(self):
        return f'{self._g} mod {self._p}'

    @property
    def identity(self):
        return GroupOfUnits(1, self._p)

    def is_identity(self):
        return self == self.identity
