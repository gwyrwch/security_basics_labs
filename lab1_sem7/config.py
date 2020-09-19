def string_to_bin_list(st):
    bin_str = ''.join('{0:08b}'.format(ord(x), 'b') for x in st)
    ans = list(bin_str)
    ans = [int(i) for i in ans]
    return ans


def bin_list_to_string(lst):
    if len(lst) % 8:
        return '---'
        raise RuntimeError(str(lst))
    res = ''
    for i in range(0, len(lst), 8):
        x = 0
        for j in range(i, i + 8):
            x = x * 2 + lst[j]
        res += chr(x)
    return res


class COLOR:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'