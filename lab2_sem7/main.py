from STB import STB
from lab1_sem7.config import *


def read_from_file(fname):
    file = open(fname, 'r')
    return file.read()


if __name__ == '__main__':
    data = read_from_file('input.txt')
    KEY = 'FKJFLKEJF1234563FEFNWNKLQL135676'

    stb = STB()
    # data = [0 for i in range(128)]
    # enc = stb.encrypt_128(data, string_to_bin_list(KEY))
    # print(enc)
    # dec = stb.decrypt_128(enc, string_to_bin_list(KEY))
    # print(dec)

    x = 'B194BAC80A08F53B366D008E584A5DE4'
    x = stb.reorder(stb.to_list(int(x, 16)))

    key = 'E9DEE72C8F0C0FA62DDB49F46F73964706075316ED247A3739CBA38303A98BF6'
    key = stb.reorder(stb.to_list(int(key, 16)))


    # enc = stb.encrypt(string_to_bin_list(data), string_to_bin_list(KEY))
    # print(enc)
    # dec = stb.decrypt(enc, string_to_bin_list(KEY))
    # print(dec)
    # print(bin_list_to_string(dec))

    enc = stb.encrypt_128(x, key)
    dec = stb.decrypt_128(enc, key)
