from collections import Counter


class STB:
    def __init__(self):
        self.H = [
            [177, 148, 186, 200, 10, 8, 245, 59, 54, 109, 0, 142, 88, 74, 93, 228],
            [133, 4, 250, 157, 27, 182, 199, 172, 37, 46, 114, 194, 2, 253, 206, 13],
            [91, 227, 214, 18, 23, 185, 97, 129, 254, 103, 134, 173, 113, 107, 137, 11],
            [92, 176, 192, 255, 51, 195, 86, 184, 53, 196, 5, 174, 216, 224, 127, 153],
            [225, 43, 220, 26, 226, 130, 87, 236, 112, 63, 204, 240, 149, 238, 141, 241],
            [193, 171, 118, 56, 159, 230, 120, 202, 247, 198, 248, 96, 213, 187, 156, 79],
            [243, 60, 101, 123, 99, 124, 48, 106, 221, 78, 167, 121, 158, 178, 61, 49],
            [62, 152, 181, 110, 39, 211, 188, 207, 89, 30, 24, 31, 76, 90, 183, 147],
            [233, 222, 231, 44, 143, 12, 15, 166, 45, 219, 73, 244, 111, 115, 150, 71],
            [6, 7, 83, 22, 237, 36, 122, 55, 57, 203, 163, 131, 3, 169, 139, 246],
            [146, 189, 155, 28, 229, 209, 65, 1, 84, 69, 251, 201, 94, 77, 14, 242],
            [104, 32, 128, 170, 34, 125, 100, 47, 38, 135, 249, 52, 144, 64, 85, 17],
            [190, 50, 151, 19, 67, 252, 154, 72, 160, 42, 136, 95, 25, 75, 9, 161],
            [126, 205, 164, 208, 21, 68, 175, 140, 165, 132, 80, 191, 102, 210, 232, 138],
            [162, 215, 70, 82, 66, 168, 223, 179, 105, 116, 197, 81, 235, 35, 41, 33],
            [212, 239, 217, 180, 58, 98, 40, 117, 145, 20, 16, 234, 119, 108, 218, 29]
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
            keys.append(key[i:i + 32])
        return keys

    def encrypt(self, data, key):
        if type(data) != list:
            raise RuntimeError('Not list')

        key = self.add_zeros(key, 256)

        data = [1] + data
        n = len(data)
        m = 0
        while m < n:
            m += 128
        data = self.add_zeros(data, m)
        res = []
        for i in range(0, m, 128):
            res += self.encrypt_128(data[i:i+128], key)
        return res

    def encrypt_128(self, data, key):
        x = []

        for i in range(0, 128, 32):
            x.append(data[i:i+32])
        a, b, c, d = x[0], x[1], x[2], x[3]

        keys = self.get_8_keys(key)
        tact_keys = []

        for i in range(7):
            tact_keys += keys

        for i in range(8):
            ak = (self.to_int(a) + self.to_int(tact_keys[7 * (i + 1) - 6 - 1])) % (2 ** 32)
            ak = self.g(self.add_zeros(self.to_list(ak), 32), 5)
            for j in range(32):
                b[j] = b[j] ^ ak[j]

            # 2) step 2
            dk = (self.to_int(d) + self.to_int(tact_keys[7 * (i + 1) - 5 - 1])) % (2 ** 32)
            dk = self.g(self.add_zeros(self.to_list(dk), 32), 21)
            for j in range(32):
                c[j] = c[j] ^ dk[j]

            # 3) step 3
            bk = (self.to_int(b) + self.to_int(tact_keys[7 * (i + 1) - 4 - 1])) % (2 ** 32)
            bk = self.g(self.add_zeros(self.to_list(bk), 32), 13)
            diff = self.to_int(a) - self.to_int(bk)
            if diff < 0:
                diff += 2 ** 32
            a = self.add_zeros(self.to_list(diff), 32)

            # 4) step 4
            e = [0 for _ in range(32)]
            bck = (self.to_int(b) + self.to_int(c) + self.to_int(tact_keys[7 * (i + 1) - 3 - 1])) % (2 ** 32)
            bck = self.g(self.add_zeros(self.to_list(bck), 32), 21)
            i_mod = self.add_zeros(self.to_list(i + 1), 32)
            for j in range(32):
                e[j] = bck[j] ^ i_mod[j]


            # 5) step 5
            be = (self.to_int(b) + self.to_int(e)) % (2 ** 32)
            b = self.add_zeros(self.to_list(be), 32)


            # 6) step 6
            ce = self.to_int(c) - self.to_int(e)
            if ce < 0:
                ce += 2 ** 32
            c = self.add_zeros(self.to_list(ce), 32)

            # 7) step 7
            ck = (self.to_int(c) + self.to_int(tact_keys[7 * (i + 1) - 2 - 1])) % (2 ** 32)
            ck = self.g(self.add_zeros(self.to_list(ck), 32), 13)
            d = self.add_zeros(
                self.to_list((self.to_int(d) + self.to_int(ck)) % (2 ** 32)),
                32
            )

            # 8) self.add_zeros(self.to_list(be), 32)step 8
            ak = (self.to_int(a) + self.to_int(tact_keys[7 * (i + 1) - 1 - 1])) % (2 ** 32)
            ak = self.g(self.add_zeros(self.to_list(ak), 32), 21)
            for j in range(32):
                b[j] = b[j] ^ ak[j]

            # 9) step 9
            dk = (self.to_int(d) + self.to_int(tact_keys[7 * (i + 1) - 1])) % (2 ** 32)
            dk = self.g(self.add_zeros(self.to_list(dk), 32), 5)
            for j in range(32):
                c[j] = c[j] ^ dk[j]

            a, b = b, a
            c, d = d, c
            b, c = c, b

        return b + d + a + c

    @staticmethod
    def to_int(lst):
        return int("".join(str(_) for _ in lst), 2)

    @staticmethod
    def to_list(n):
        return [int(i) for i in "{0:b}".format(n)]

    def decrypt(self, data, key):
        if type(data) != list:
            raise RuntimeError('Not a list')
        if len(data) % 128:
            raise RuntimeError('Wrong size')
        if type(data) != list:
            raise RuntimeError('Not list')

        n = len(data)
        key = self.add_zeros(key, 256)
        res = []
        for i in range(0, n, 128):
            res += self.decrypt_128(data[i:i + 128], key)

        while res[0] != 1:
            res = res[1:]
        return res[1:]

    def decrypt_128(self, data, key):
        x = []
        for i in range(0, 128, 32):
            x.append(data[i:i + 32])
        a, b, c, d = x[0], x[1], x[2], x[3]

        keys = self.get_8_keys(key)
        tact_keys = []
        for i in range(7):
            tact_keys += keys

        for i in range(7, -1, -1):
            # 1) step 1
            ak = (self.to_int(a) + self.to_int(tact_keys[7 * (i + 1) - 1])) % (2 ** 32)
            ak = self.g(self.add_zeros(self.to_list(ak), 32), 5)
            for j in range(32):
                b[j] = b[j] ^ ak[j]

            # 2) step 2
            dk = (self.to_int(d) + self.to_int(tact_keys[7 * (i + 1) - 1 - 1])) % 2 ** 32
            dk = self.g(self.add_zeros(self.to_list(dk), 32), 21)
            for j in range(32):
                c[j] = c[j] ^ dk[j]

            # 3) step 3
            bk = (self.to_int(b) + self.to_int(tact_keys[7 * (i + 1) - 2 - 1])) % (2 ** 32)
            bk = self.g(self.add_zeros(self.to_list(bk), 32), 13)
            diff = self.to_int(a) - self.to_int(bk)
            if diff < 0:
                diff += 2 ** 32
            a = self.add_zeros(self.to_list(diff), 32)

            # 4) step 4
            e = [0 for _ in range(32)]
            bck = (self.to_int(b) + self.to_int(c) + self.to_int(tact_keys[7 * (i + 1) - 3 - 1])) % (2 ** 32)
            bck = self.g(self.add_zeros(self.to_list(bck), 32), 21)
            i_mod = self.add_zeros(self.to_list(i + 1), 32)
            for j in range(32):
                e[j] = bck[j] ^ i_mod[j]

            # 5) step 5
            be = (self.to_int(b) + self.to_int(e)) % (2 ** 32)
            b = self.add_zeros(self.to_list(be), 32)

            # 6) step 6
            ce = self.to_int(c) - self.to_int(e)
            if ce < 0:
                ce += 2 ** 32
            c = self.add_zeros(self.to_list(ce), 32)

            # 7) step 7
            ck = (self.to_int(c) + self.to_int(tact_keys[7 * (i + 1) - 4 - 1])) % (2 ** 32)
            ck = self.g(self.add_zeros(self.to_list(ck), 32), 13)
            d = self.add_zeros(
                self.to_list((self.to_int(d) + self.to_int(ck)) % (2 ** 32)),
                32
            )

            # 8) step 8
            ak = (self.to_int(a) + self.to_int(tact_keys[7 * (i + 1) - 5 - 1])) % (2 ** 32)
            ak = self.g(self.add_zeros(self.to_list(ak), 32), 21)
            for j in range(32):
                b[j] = b[j] ^ ak[j]

            # 9) step 9
            dk = (self.to_int(d) + self.to_int(tact_keys[7 * (i + 1) - 6 - 1])) % (2 ** 32)
            dk = self.g(self.add_zeros(self.to_list(dk), 32), 5)
            for j in range(32):
                c[j] = c[j] ^ dk[j]

            a, b = b, a
            c, d = d, c
            a, d = d, a

        return c + a + d + b

    def g(self, u, r):
        if r != 5 and r != 13 and r != 21:
            raise RuntimeError('Invalid param r')

        if len(u) != 32:
            raise RuntimeError('Invalid u len')

        x = []
        for i in range(0, 32, 8):
            x.append(u[i:i+8])

        res = []
        for u_i in x:
            u_ir = self.to_int(u_i[:4])
            u_ic = self.to_int(u_i[4:])

            res += self.add_zeros(
                self.to_list(self.H[u_ir][u_ic]),
                8
            )

        if len(res) != 32:
            raise RuntimeError('Invalid res len after operations made in G')

        return res[r:] + res[:r]

    def reorder_internal(self, data):
        if len(data) != 32:
            raise RuntimeError
        res = [0]*32
        res[0:8] = data[24:32]
        res[8:16] = data[16:24]
        res[16:24] = data[8:16]
        res[24:32] = data[0:8]
        return res

    def reorder(self, data):
        if len(data) % 32:
            raise RuntimeError('Wrong size in reorder')
        for i in range(0, len(data), 32):
            data[i:i+32] = self.reorder_internal(data[i:i+32])
        return data

    def print_with_reorder(self, val):
        if len(val) != 32:
            raise RuntimeError
        print(hex(self.to_int(self.reorder_internal(val))))