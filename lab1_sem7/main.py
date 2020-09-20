from DoubleDes import DoubleDes
from TripleDes import TripleDes
from GOST import GOST
from config import string_to_bin_list, bin_list_to_string


def read_from_file(fname):
    file = open(fname, 'r')
    return file.read()


if __name__ == '__main__':
    data = read_from_file('input.txt')
    KEY = '12345678'
    KEY2 = 'KILLALL'

    # double_des = DoubleDes(KEY, KEY2)
    # double_des.encrypt_and_decrypt(data, True)

    # triple_des = TripleDes(KEY, KEY2)
    # triple_des.encrypt_and_decrypt(data, True)
    # x = []
    # keys = [1,2,3,4,5,6,7,8]
    # for i in range(8):
    #     x.append(keys[i])

    # for i in range(24):
    #     x.append(keys[(7 - i) % 8])
    # print(x)

    KEY = 'FKJFLKEJF1234563FEFNWNKLQL135676'
    gost = GOST()
    print(data)

    # datalist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #  0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1]
    # enc = gost.encrypt_64(datalist, gost.get_8_keys(gost.add_zeros(string_to_bin_list(KEY), 256)))
    # print(gost.decrypt_64(enc, gost.get_8_keys(gost.add_zeros(string_to_bin_list(KEY), 256))))

    enc = gost.encrypt(string_to_bin_list(data), string_to_bin_list(KEY))
    dec = gost.decrypt(enc, string_to_bin_list(KEY))
    print(bin_list_to_string(dec))
    #
    print(len(enc), len(string_to_bin_list(data)), len(dec))




