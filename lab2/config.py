import json

IP = '127.0.0.1'
AS_PORT = 20001
TGS_PORT = 20008
buffer_size = 16384

SERVER_PORT = 20009


def string_to_bin_list(st):
    bin_str = ''.join('{0:08b}'.format(ord(x), 'b') for x in st)
    ans = list(bin_str)
    ans = [int(i) for i in ans]
    return ans


def bin_list_to_string(lst):
    if len(lst) % 8:
        print(lst)
        raise RuntimeError(str(lst))
    res = ''
    for i in range(0, len(lst), 8):
        x = 0
        for j in range(i, i + 8):
            x = x * 2 + lst[j]
        res += chr(x)
    return res


def json_to_bin_list(j):
    return string_to_bin_list(json.dumps(j))

