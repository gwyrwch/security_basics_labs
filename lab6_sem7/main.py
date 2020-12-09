from lab6_sem7.GOST_3410 import *
from lab6_sem7.GOST_3411 import Gost3411


def prepare_hash(bytes_object):
    gost3411 = Gost3411()
    return gost3411.get_hash(bytes_object).hex()


if __name__ == '__main__':
    hash_value_sign = prepare_hash(b'001ab01')
    hash_value_test = prepare_hash(b'001a3b01')

    print('HASH value of signature is {}'.format('\033[94m' + hash_value_sign + '\033[0m'))
    print('HASH value of test is {}'.format('\033[94m' + hash_value_test + '\033[0m'))

    curve = Curve()
    privkey = private_key()
    pubkey = public_key(curve, privkey)

    gost = Gost3410()
    signature = gost.sign(curve, privkey, int(hash_value_sign, 16))

    is_verified = gost.verify(curve, pubkey, int(hash_value_test, 16), signature)

    print('Is signature verified: {}'.format('\033[94m' + str(is_verified) + '\033[0m'))
