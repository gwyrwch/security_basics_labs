
def tobin(x, need_len):
    x = bin(x)[2:]
    assert len(x) <= need_len
    if len(x) < need_len:
        x = '0' * (need_len - len(x)) + x
    return x


def iptobin(ip):
    tokens = ip.split('.')

    for i, t in enumerate(tokens):
        tokens[i] = tobin(int(t), 8)

    return ''.join(tokens)


def checksum16(msg):
    assert len(msg) % 16 == 0
    result = 0
    for i in range(0, len(msg), 16):
        result += int(msg[i:i+16], 2)
    result %= 65536
    return tobin(result, 16)


def build_tcp_message(
    port_from,
    port_to,
    sequence_number='0'*32,
    acknowledgment_number='0'*32,
    tcp_header_len='0'*4,
    urg='0', ack='0', psh='0', rst='0', syn='0', fin='0',
    window_size='0'*16,
    urgency='0'*16,
    data='0'*32
):
    checksum = '0'*16
    port_from = tobin(port_from, 16)
    port_to = tobin(port_to, 16)

    tmp_msg = ''.join([
        port_from, port_to, sequence_number, acknowledgment_number, tcp_header_len, '0'*6, urg, ack, psh, rst, syn, fin,
        window_size, checksum, urgency, '0'*32, data
    ])
    checksum = checksum16(tmp_msg)

    return ''.join([
        port_from, port_to, sequence_number, acknowledgment_number, tcp_header_len, '0'*6, urg, ack, psh, rst, syn, fin,
        window_size, checksum, urgency, '0'*32, data
    ])


def build_ip_message(
    version='0100',
    ip_header_len='0000',
    type_of_service='0'*8,
    datagram_id='0'*16,
    flags='0'*3,
    fragment_pointer='0'*13,
    ttl='01000001',
    proto='00000110',
    ip_from=None,
    ip_to=None,
    ip_params='0'*32,
    data=None
):
    if ip_from and ip_to and data:
        checksum = '0'*16
        ip_from = iptobin(ip_from)
        ip_to = iptobin(ip_to)
        package_size = tobin(24 + len(data) // 8, 16)
        tmp_msg = ''.join([
            version, ip_header_len, type_of_service, package_size, datagram_id, flags, fragment_pointer, ttl,
            proto, checksum, ip_from, ip_to, ip_params, data

        ])

        checksum = checksum16(tmp_msg)
        return ''.join([
            version, ip_header_len, type_of_service, package_size, datagram_id, flags, fragment_pointer, ttl,
            proto, checksum, ip_from, ip_to, ip_params, data

        ])
    else:
        raise


def bintoip(ip_bin):
    assert len(ip_bin) == 32
    res = ''
    for i in range(4):
        x = ip_bin[i*8:(i+1)*8]
        if i:
            res += '.'
        res += str(int(x, 2))
    return res


def valid_checksum(msg, checksum, l, r):
    msg2 = msg[:l] + '0' * (r - l) + msg[r:]
    assert len(msg2) == len(msg)
    return checksum16(msg2) == checksum


def tcp_ip_checks(m, my_ip):
    if not m['result']:
        print(m['comment'])
        return False
    if m['ip_to'] != my_ip:
        print('wrong destination ip exp {}, got {}'.format(my_ip, m['ip_to']))
        return False
    if m['ttl'] <= 0:
        print('ttl is 0')
        return False
    return True


def parse_tcp_ip_message(msg):
    ip_header = msg[:6 * 32]
    tcp_msg = msg[6 * 32:]

    ip_from = bintoip(ip_header[3 * 32:4 * 32])
    ip_to = bintoip(ip_header[4 * 32:5 * 32])
    ttl = int(ip_header[2 * 32:2 * 32 + 8], 2)
    ip_checksum = ip_header[2 * 32 + 16:3 * 32]
    if not valid_checksum(msg, ip_checksum, 2 * 32 + 16, 3 * 32):
        return {
            'result': False,
            'comment': 'ip checksum invalid'
        }

    port_from = int(tcp_msg[0:16], 2)
    port_to = int(tcp_msg[16:32], 2)
    sequence_number = tcp_msg[32:64]
    acknowledgment_number = tcp_msg[64:3 * 32]
    urg = tcp_msg[3 * 32 + 10]
    ack = tcp_msg[3 * 32 + 11]
    psh = tcp_msg[3 * 32 + 12]
    rst = tcp_msg[3 * 32 + 13]
    syn = tcp_msg[3 * 32 + 14]
    fin = tcp_msg[3 * 32 + 15]
    data = tcp_msg[-32:]

    tcp_checksum = tcp_msg[4 * 32:4 * 32 + 16]
    if not valid_checksum(tcp_msg, tcp_checksum, 4 * 32, 4 * 32 + 16):
        return {
            'result': False,
            'comment': 'tcp checksum invalid'
        }

    return {
        'result': True,
        'ip_from': ip_from,
        'ip_to': ip_to,
        'ttl': ttl,
        'port_from': port_from,
        'port_to': port_to,
        'sequence_number': sequence_number,
        'acknowledgment_number': acknowledgment_number,
        'urg': urg, 'ack': ack, 'psh': psh, 'rst': rst, 'syn': syn, 'fin': fin,
        'data': data
    }
