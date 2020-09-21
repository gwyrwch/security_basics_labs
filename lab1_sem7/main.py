from DoubleDes import DoubleDes
from TripleDes import TripleDes
from GOST import GOST
from config import string_to_bin_list, bin_list_to_string, COLOR


def read_from_file(fname):
    file = open(fname, 'r')
    return file.read()


if __name__ == '__main__':
    data = read_from_file('input.txt')
    KEY = '1234567'
    KEY2 = 'KILLAL'
    print(COLOR.FAIL + 'DOUBLE DES' + COLOR.ENDC)
    double_des = DoubleDes(KEY, KEY2)
    double_des.encrypt_and_decrypt(data, True)

    print('\n' + COLOR.FAIL + 'TRIPLE DES' + COLOR.ENDC)
    triple_des = TripleDes(KEY, KEY2)
    triple_des.encrypt_and_decrypt(data, True)

    print('\n' + COLOR.FAIL + 'GOST' + COLOR.ENDC)
    KEY3 = 'FKJFLKEJF1234563FEFNWNKLQL135676'
    gost = GOST()

    enc = gost.encrypt(string_to_bin_list(data), string_to_bin_list(KEY3))

    dec = gost.decrypt(enc, string_to_bin_list(KEY3))
    print('KEY: ' + COLOR.OKBLUE + KEY3 + COLOR.ENDC)
    print('Text: ' + COLOR.HEADER + data + COLOR.ENDC)
    print('Encoded string: ' + COLOR.HEADER + bin_list_to_string(enc) + COLOR.ENDC)
    print(COLOR.ENDC + 'Decoded string: ' + COLOR.HEADER + bin_list_to_string(dec) + COLOR.ENDC)




