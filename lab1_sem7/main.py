from DoubleDes import DoubleDes
from TripleDes import TripleDes


def read_from_file(fname):
    file = open(fname, 'r')
    return file.read()


if __name__ == '__main__':
    data = read_from_file('input.txt')
    KEY = '1234567'
    KEY2 = 'KILLALL'

    # double_des = DoubleDes(KEY, KEY2)
    # double_des.encrypt_and_decrypt(data, True)

    triple_des = TripleDes(KEY, KEY2)
    triple_des.encrypt_and_decrypt(data, True)




