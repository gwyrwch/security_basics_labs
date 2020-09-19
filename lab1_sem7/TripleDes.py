from DES import DES
from config import *


class TripleDes:
    def __init__(self, key1, key2):
        if key1 is None or key2 is None:
            raise RuntimeError('keys must not be none')

        self.KEY1 = key1
        self.KEY2 = key2
        self.des = DES()

    def encrypt_and_decrypt(self, data, output=False):
        enc1 = self.des.encrypt(string_to_bin_list(data), string_to_bin_list(self.KEY1))
        dec2 = self.des.decrypt(enc1, string_to_bin_list(self.KEY2))
        enc1_2 = self.des.encrypt(dec2, string_to_bin_list(self.KEY1))

        dec1 = self.des.decrypt(enc1_2, string_to_bin_list(self.KEY1))
        enc2 = self.des.encrypt(dec1, string_to_bin_list(self.KEY2))
        dec1_2 = self.des.decrypt(enc2, string_to_bin_list(self.KEY1))

        if output:
            print(COLOR.OKBLUE + data + COLOR.ENDC)
            print('KEY1 = {}, KEY2 = {}'.format(self.KEY1, self.KEY2))
            print('Encoded data with KEY1 ' + COLOR.HEADER + '{}'.format(bin_list_to_string(enc1)) + COLOR.ENDC)
            print('Decoded data with KEY2 ' + COLOR.HEADER + '{}'.format(bin_list_to_string(dec2)) + COLOR.ENDC)
            print(
                'Encoded data with KEY1 after decoding with KEY2 ' +
                COLOR.HEADER +
                '{}'.format(bin_list_to_string(enc1_2)) +
                COLOR.ENDC
            )
            print(COLOR.FAIL + 'encoded' + COLOR.ENDC)
            print(
                'Decoded data with KEY1 ' +
                COLOR.HEADER +
                '{}'.format(bin_list_to_string(dec1)) +
                COLOR.ENDC
            )
            print(
                'Encoded data with KEY2 ' +
                COLOR.HEADER +
                '{}'.format(bin_list_to_string(enc2)) +
                COLOR.ENDC
            )
            print(
                'Decoded data with KEY1 after encoding with KEY2 ' +
                COLOR.HEADER +
                '{}'.format(bin_list_to_string(dec1_2)) +
                COLOR.ENDC
            )
            print(COLOR.FAIL + 'decoded' + COLOR.ENDC)


