from hashlib import sha256
import random


def euclid(sml, big):
    if sml == 0:
        return (big, 0, 1)
    else:
        g, y, x = euclid(big % sml, sml)
        return (g, x - (big//sml)*y, y)


def mult_inv(a, n):
    g, x, y = euclid(a, n)
    return x % n


class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.inf = False

    @classmethod
    def atInfinity(cls):
        P = cls(0, 0)
        P.inf = True
        return P

    @classmethod
    def secp256k1(cls):
        return cls(55066263022277343669578718895168534326250603453777594175500187360389116729240,
                   32670510020758816978083085130507043184471273380659243275938904335757337482424)

    def __eq__(self, other):
        if self.inf:
            return other.inf
        elif other.inf:
            return self.inf
        else:
            return self.x == other.x and self.y == other.y

    def is_infinite(self):
        return self.inf


class Curve(object):
    #Set attributes of a general Weierstrass cubic y^2 = x^3 + ax^2 + bx + c over any field.
    def __init__(self, a, b, c, char, exp):
        self.a, self.b, self.c = a, b, c
        self.char, self.exp = char, exp

    def mult(self, P, k):
        if P.is_infinite():
            return P
        elif k == 0:
            return Point.atInfinity()
        elif k < 0:
            return self.mult(self.invert(P), -k)
        else:
            b = bin(k)[2:]
            return self.repeat_additions(P, b, 1)

    def repeat_additions(self, P, b, n):
        if b == '0':
            return Point.atInfinity()
        elif b == '1':
            return P
        elif b[-1] == '0':
            return self.repeat_additions(self.add(P, P), b[:-1], n+1)
        elif b[-1] == '1':
            return self.add(P, self.repeat_additions(self.add(P, P), b[:-1], n+1))


class CurveOverFp(Curve):
    #Construct a Weierstrass cubic y^2 = x^3 + ax^2 + bx + c over Fp.
    def __init__(self, a, b, c, p):
        Curve.__init__(self, a, b, c, p, 1)

    #The secp256k1 curve.
    @classmethod
    def secp256k1(cls):
        return cls(0, 0, 7, 2**256-2**32-2**9-2**8-2**7-2**6-2**4-1)

    def contains(self, P):
        if P.is_infinite():
            return True
        else:
            return (P.y*P.y) % self.char == (P.x*P.x*P.x + self.a*P.x*P.x + self.b*P.x + self.c) % self.char

    def invert(self, P):
        if P.is_infinite():
            return P
        else:
            return Point(P.x, -P.y % self.char)

    def add(self, P_1, P_2):
        y_diff = (P_2.y - P_1.y) % self.char
        x_diff = (P_2.x - P_1.x) % self.char
        if P_1.is_infinite():
            return P_2
        elif P_2.is_infinite():
            return P_1
        elif x_diff == 0 and y_diff != 0:
            return Point.atInfinity()
        elif x_diff == 0 and y_diff == 0:
            if P_1.y == 0:
                return Point.atInfinity()
            else:
                ld = ((3*P_1.x*P_1.x + 2*self.a*P_1.x + self.b) * mult_inv(2*P_1.y, self.char)) % self.char
        else:
            ld = (y_diff * mult_inv(x_diff, self.char)) % self.char
        nu = (P_1.y - ld*P_1.x) % self.char
        x = (ld*ld - self.a - P_1.x - P_2.x) % self.char
        y = (-ld*x - nu) % self.char
        return Point(x, y)


def hash(message):
    return int(sha256(message).hexdigest(), 16)


def hash_and_cut(message, n):
    h = hash(message)
    b = bin(h)[2:len(bin(n))]
    return int(b, 2)


def prepare_keys(curve, P, n):
    d = random.randrange(1, n)
    Q = curve.mult(P, d)
    print("Private key: d = " + str(d))
    print("Public key: Q = " + str(Q.x) + ',' + str(Q.y))
    return d, Q


def sign(message, curve, P, n, private, public):
    d, Q = private, public
    z = hash_and_cut(message, n)
    r, s = 0, 0
    while r == 0 or s == 0:
        k = 4
        R = curve.mult(P, k)
        r = R.x % n
        s = (mult_inv(k, n) * (z + r*d)) % n
    return Q, r, s


def verify(message, curve, P, n, signature):
    Q, r, s = signature
    if Q.is_infinite() or not curve.contains(Q):
        return False
    if not curve.mult(Q, n).is_infinite():
        return False
    if r > n or s > n:
        return False
    z = hash_and_cut(message, n)
    w = mult_inv(s, n) % n
    u_1, u_2 = z * w % n, r * w % n
    C_1, C_2 = curve.mult(P, u_1), curve.mult(Q, u_2)
    C = curve.add(C_1, C_2)
    return r % n == C.x % n


def encode(curve, G, Pm, Pb):
    k = random.randrange(1, 10000)
    return curve.mult(G, k), curve.add(curve.mult(Pb, k), Pm)


def decode(curve, P1, P2, nb):
    return curve.add(P2, curve.invert(curve.mult(P1, nb)))