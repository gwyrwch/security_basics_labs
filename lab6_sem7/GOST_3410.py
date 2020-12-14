import os


p_bytes = "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdc7"
q_bytes = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff27e69532f48d89116ff22b8d4e0560609b4b38abfad2b85dcacdb1411f10b275"
a_bytes = "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdc4"
b_bytes = "e8c2505dedfc86ddc1bd0b2b6667f1da34b82574761cb0e879bd081cfd0b6265ee3cb090f30d27614cb4574010da90dd862ef9d4ebee4761503190785a71c760"
x_bytes = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003"
y_bytes = "7503cfe87a836ae3a61b8816e25450e6ce5e1c93acf1abc1778064fdcbefa921df1626be4fd036e93d75e6a50e3a41e98028fe5fc235f5b889a589cb5215f2a4"


def inv(x, mod):
    assert x >= 0
    t, newt = 0, 1
    r, newr = mod, x
    while newr != 0:
        q = r // newr
        t, newt = newt, t - q * newt
        r, newr = newr, r - q * newr
    assert r <= 1
    if t < 0:
        t = t + mod
    return t


class Curve:
    def __init__(self):
        self.p = 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006083527
        self.q = 13407807929942597099574024998205846127479365820592393377723561443721764030073449232318290585817636498049628612556596899500625279906416653993875474742293109
        self.a = 13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006083524
        self.b = 12190580024266230156189424758340094075514844064736231252208772337825397464478540423418981074322718899427039088997221609947354520590448683948135300824418144
        self.x = 3
        self.y = 6128567132159368375550676650534153371826708807906353132296049546866464545472607119134529221703336921516405107369028606191097747738367571924466694236795556

    def add(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            t = ((3 * x1 * x1 + self.a) * inv(2 * y1, self.p)) % self.p
        else:
            tx = ((x2 - x1) % self.p + self.p) % self.p
            ty = ((y2 - y1) % self.p + self.p) % self.p
            t = (ty * inv(tx, self.p)) % self.p
        tx = ((t * t - x1 - x2) % self.p + self.p) % self.p
        ty = (t * (x1 - tx) - y1) % self.p
        return tx, ty

    def exp(self, n, x=None, y=None):
        x = x or self.x
        y = y or self.y
        ax = x
        ay = y
        n -= 1
        assert n != 0

        while n > 0:
            if n % 2:
                ax, ay = self.add(ax, ay, x, y)
            x, y = self.add(x, y, x, y)
            n //= 2
        return ax, ay


def public_key(curve, private):
    return curve.exp(private)


def private_key():
    return int(os.urandom(128).hex(), 16)


class Gost3410:
    def __init__(self):
        pass

    def sign(self, curve, private, z):
        # z (hash) -- int
        # curve Curve
        # private int

        q = curve.q
        e = z % q
        if e == 0:
            e = 1

        s = 0
        r = 0
        while s == 0:
            k = int(os.urandom(64).hex(), 16) % (q - 1) + 1
            r, _ = curve.exp(k)
            r %= q
            if r == 0:
                continue
            s = (r * private + k * e) % q
        return r, s

    def verify(self, curve, pub, z, signature):
        # z int -- hash
        # signature (int, int) r, s
        # pub (x, y)

        r, s = signature
        q = curve.q

        if r <= 0 or r >= q or s <= 0 or s >= q:
            return False

        e = z % curve.q
        if e == 0:
            e = 1
        v = inv(e, q)
        z1 = s * v % q
        z2 = (q - r * v % q) % q
        p1x, p1y = curve.exp(z1)
        q1x, q1y = curve.exp(z2, pub[0], pub[1])

        R, _ = curve.add(p1x, p1y, q1x, q1y)
        R %= q
        return R == r


