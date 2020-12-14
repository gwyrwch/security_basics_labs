from lab7_sem7.ECDSA import *

if __name__ == '__main__':
    # y^2 = x^3 + 7
    C = CurveOverFp.secp256k1()

    P = Point.secp256k1()
    n = 115792089237316195423570985008687907852837564279074904382605163141518161494337

    priv, public = prepare_keys(C, P, n)
    msg = b'001'
    sig = sign(msg, C, P, n, priv, public)
    print(verify(b'001', C, P, n, sig))
    print(verify(b'224', C, P, n, sig))

    priv, public =prepare_keys(C, P, n)
    # encoding

    print('\nENCODING/DECODING')
    print('Point to encode: P = {}, {}'.format(P.x, P.y))
    enc_pts = encode(C, P, P, public)
    print('ENCODING: \nP1 = {}, {}\nP2 = {}, {}'.format(enc_pts[0].x, enc_pts[0].y, enc_pts[1].x, enc_pts[1].y))
    decpt = decode(C, enc_pts[0], enc_pts[1], priv)
    print('DECODING: P = {}, {}'.format(decpt.x, decpt.y))
