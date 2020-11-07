from STB import STB
from lab1_sem7.config import *


def read_from_file(fname):
    file = open(fname, 'r')
    return file.read()


if __name__ == '__main__':
    stb = STB()

    data = read_from_file('input.txt')
    KEY = 'FKJFLKEJF1234563FEFNWNKLQL135676'
    s = 'A12D1AC90908F53B366D098E584A5DE4'

    print('Text to encrypt and decrypt: ' + COLOR.HEADER + data + COLOR.ENDC)
    print('KEY: ' + COLOR.HEADER + KEY + COLOR.ENDC)
    print('S: ' + COLOR.HEADER + s + COLOR.ENDC)

    s = stb.reorder(stb.to_list(int(s, 16)))
    # key = 'E9DEE72C8F0C0FA62DDB49F46F73964706075316ED247A3739CBA38303A98BF6'
    # key = stb.reorder(stb.to_list(int(key, 16)))

    print(COLOR.OKBLUE + 'Simple replace mode' + COLOR.ENDC)
    enc = stb.encrypt(string_to_bin_list(data), string_to_bin_list(KEY))
    print('ENCRYPTED: ' + COLOR.BOLD + bin_list_to_string(enc) + COLOR.ENDC)
    dec = stb.decrypt(enc, string_to_bin_list(KEY))
    print('DECRYPTED: ' + COLOR.BOLD + bin_list_to_string(dec) + COLOR.ENDC)

    print(COLOR.OKBLUE + 'Encryption in block chaining mode' + COLOR.ENDC)
    enc = stb.encrypt_in_chaining_mode(string_to_bin_list(data), string_to_bin_list(KEY), s)
    print('ENCRYPTED: ' + COLOR.BOLD + bin_list_to_string(enc) + COLOR.ENDC)
    dec = stb.decrypt_from_chaining_mode(enc, string_to_bin_list(KEY), s)
    print(COLOR.ENDC + 'DECRYPTED: ' + COLOR.BOLD + bin_list_to_string(dec) + COLOR.ENDC)

    print(COLOR.OKBLUE + 'Encryption in gamma mode' + COLOR.ENDC)
    enc = stb.encrypt_in_gamma_mode(string_to_bin_list(data), string_to_bin_list(KEY), s)
    print('ENCRYPTED: ' + COLOR.BOLD + bin_list_to_string(enc) + COLOR.ENDC)
    dec = stb.decrypt_from_gamma_mode(enc, string_to_bin_list(KEY), s)
    print('DECRYPTED: ' + COLOR.BOLD + bin_list_to_string(dec) + COLOR.ENDC)

    print(COLOR.OKBLUE + 'Encryption in counter mode' + COLOR.ENDC)
    enc = stb.encrypt_in_counter_mode(string_to_bin_list(data), string_to_bin_list(KEY), s)
    enc_str = bin_list_to_string(enc)
    enc_str0 = ''
    for i in range(len(enc_str)):
        enc_str0 += enc_str[i] if enc_str[i] != '\r' else ' '

    print('ENCRYPTED:' + COLOR.BOLD + enc_str0 + COLOR.ENDC)
    dec = stb.decrypt_from_counter_mode(enc, string_to_bin_list(KEY), s)
    print('DECRYPTED: ' + COLOR.BOLD + bin_list_to_string(dec) + COLOR.ENDC)

