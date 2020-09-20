from collections import Counter


class GOST:
    def __init__(self):
        self.S = [
            [4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3],
            [14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9],
            [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11],
            [7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3],
            [6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2],
            [4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14],
            [13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12],
            [1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12]
        ]

    @staticmethod
    def add_zeros(data, k):
        if len(data) <= k:
            zeros_size = k - len(data)
            data2 = [0 for i in range(zeros_size)] + data
            return data2
        elif len(data) > k:
            raise RuntimeError('{}, {}'.format(len(data), k))

    @staticmethod
    def get_8_keys(key):
        if len(key) != 256:
            raise RuntimeError('Key size is {} not 256'.format(len(key)))

        keys = []
        for i in range(0, 256, 32):
            keys.append(key[i:i+32])
        return keys

    def encrypt(self, data, key):
        if type(data) != list:
            raise RuntimeError('Not list')

        key = self.add_zeros(key, 256)
        keys = self.get_8_keys(key)

        data = [1] + data
        n = len(data)
        m = 0
        while m < n:
            m += 64
        data = self.add_zeros(data, m)
        res = []

        for i in range(0, m, 64):
            res += self.encrypt_64(data[i:i+64], keys)
        return res

    @staticmethod
    def get_x(keys):
        x = []

        for i in range(24):
            x.append(keys[i % 8])

        for i in range(8):
            x.append(keys[7 - i])

        if len(x) != 32:
            raise RuntimeError('invalid x size')

        return x

    @staticmethod
    def get_x_dec(keys):
        x = []

        for i in range(8):
            x.append(keys[i])

        for i in range(24):
            x.append(keys[(7 - i) % 8])

        if len(x) != 32:
            raise RuntimeError('invalid x size')

        return x

    def encrypt_64(self, data, keys):
        """
        :param data: 64 bit binary list //
        :param keys: list of size 8 with bit keys
        :return: encrypted 64 bit list
        """

        a_i = data[:32]
        b_i = data[32:]

        x = self.get_x(keys)

        for i in range(32):
            k_i = x[i]
            a_i, b_i = self.transform(a_i, b_i, k_i)

        return a_i + b_i

    def transform(self, l_prev, r_prev, k_i):
        r_i = l_prev

        l_i = [0 for i in range(32)]
        frk = self.f(l_prev, k_i)
        for i in range(32):
            l_i[i] = r_prev[i] ^ frk[i]

        return l_i, r_i

    def f(self, l, k_i):
        # print(l, k_i)
        l_int = int("".join(str(i) for i in l), 2)
        k_int = int("".join(str(i) for i in k_i), 2)
        l_k_mod = (l_int + k_int) % (2 ** 32)
        res = self.add_zeros([int(i) for i in "{0:b}".format(l_k_mod)], 32)
        # res = [0 for _ in range(32)]
        # for i in range(32):
        #     res[i] = l[i] ^ k_i[i]

        seq = []
        for i in range(0, 32, 4):
            seq.append(res[i:i+4])

        res = []
        for i in range(8):
            # print(seq[i])
            s_int = int("".join(str(i) for i in seq[i]), 2)
            # print(s_int)
            s_int = self.S[i][s_int]
            # print(s_int)
            seq[i] = self.add_zeros([int(i) for i in "{0:b}".format(s_int)], 4)
            # print(seq[i])
            res += seq[i]

        res = res[11:] + res[:11]
        if len(res) != 32:
            raise RuntimeError('res in f should have len 32')
        return res

    def decrypt(self, data, key):
        if type(data) != list:
            raise RuntimeError('Not a list')
        if len(data) % 64:
            raise RuntimeError('Wrong size')

        key = self.add_zeros(key, 256)
        keys = self.get_8_keys(key)

        n = len(data)
        res = []

        for i in range(0, n, 64):
            res += self.decrypt_64(data[i:i+64], keys)
        while res[0] != 1:
            res = res[1:]
        return res[1:]

    def decrypt_64(self, data, keys):
        """
        :param data: 64 bit binary string // in a list??
        :param keys: 56 bit key
        :return: encrypted 64 bit string
        """

        a_i = data[:32]
        b_i = data[32:]

        x = self.get_x_dec(keys)

        for i in range(32):
            k_i = x[i]
            b_i, a_i = self.transform(b_i, a_i, k_i)
        return a_i + b_i

