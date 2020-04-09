import random
import socket
import time

import config1
from util import *


class Client:
    def __init__(self, my_port, timeout=0.5):
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.port = my_port
        self.IP = config1.IP
        self.s.bind((config1.IP, self.port))
        self.s.settimeout(timeout)

    def get_msg(self):
        try:
            msg, address = self.s.recvfrom(config1.buffer_size)
        except Exception as e:
            print(e)
            return None

        return msg.decode()

    def send_to_port(self, port_to, ip_from=config1.IP, ip_to=config1.IP, port_from=None, **kwargs):
        if port_from is None:
            port_from = self.port
        tcp_msg = build_tcp_message(port_from, port_to, **kwargs)
        ip_msg = build_ip_message(ip_from=ip_from, ip_to=ip_to, data=tcp_msg)
        self.s.sendto(ip_msg.encode(), (ip_to, port_to))


def passive_scan():
    client = Client(22221)

    ccasks = 0
    misses = 0
    for port in range(20000, 20005):
        client.send_to_port(port, syn='1', sequence_number=tobin(random.randint(0, 2 ** 32 - 1), 32))
        ccasks += 1
    print('Asked all')
    to_attack_addr = set()
    for i in range(ccasks):
        msg = client.get_msg()
        if not msg:
            misses += 1
            continue
        m = parse_tcp_ip_message(msg)
        if not tcp_ip_checks(m, client.IP):
            continue
        print("GET", m)
        if m['syn'] == '1' and m['ack'] == '1':
            to_attack_addr.add(m['port_from'])

    for port in to_attack_addr:
        client.send_to_port(port, rst='1')
    print('Passive scan finished, total ports = {}, daemons found on {} ports'.format(ccasks - misses, len(to_attack_addr)))
    if len(to_attack_addr):
        print(to_attack_addr)


def tcp_reset():
    ip_to = '127.0.0.1'
    port_vict = int(input('What port to attack?\n'))

    client = Client(22223)

    for x in range(1, 10):
        ip_from = '127.0.0.{}'.format(x)
        client.send_to_port(port_vict, ip_from=ip_from, ip_to=ip_to, rst='1', port_from=22220)


def communicate():
    port_server = int(input('What port to communicate?\n'))
    client = Client(22220)

    for i in range(1000000000):
        client.send_to_port(port_server, data=tobin(i, 32))
        msg = client.get_msg()
        if not msg:
            print('No server on that port/ server did\'nt answer')
            break
        m = parse_tcp_ip_message(msg)
        if not tcp_ip_checks(m, client.IP):
            break
        print(m)
        if m['rst'] == '1':
            print('he asked to stop')
            break
        time.sleep(1)


def syn_flooding():
    port_vict = int(input('What port to attack?\n'))
    client = Client(22222)

    for x in range(2, 20):
        ip_from = '127.0.0.{}'.format(x)
        client.send_to_port(port_vict, ip_from=ip_from, syn='1', sequence_number=tobin(random.randint(0, 2 ** 32 - 1),32))


def try_start():
    port_server = int(input('What port to communicate?\n'))
    client = Client(22220)

    for i in range(10):
        client.send_to_port(port_server, syn='1', sequence_number=tobin(random.randint(0, 2 ** 32 - 1),32))
        m = client.get_msg()
        if m:
            print('Ok')

            m = parse_tcp_ip_message(m)

            seq = int(m['sequence_number'], 2)
            ack = int(m['acknowledgment_number'], 2)
            if ack == 0:
                ack = random.randint(0, 2 ** 32 - 1), 32

            seq += 1
            seq %= 2 ** 32
            seq, ack = ack, seq
            seq = tobin(seq, 32)
            ack = tobin(ack, 32)

            client.send_to_port(port_server, ack='1', sequence_number=seq,
                                acknowledgment_number=ack)
        else:
            print('\r Server didn\'t answer')
        time.sleep(1)


if __name__ == '__main__':
    mode = input('Choose attack? ps/rst/synf/rst-com/syn-com\n\r')
    if mode == 'ps':
        passive_scan()
    elif mode == 'rst':
        tcp_reset()
    elif mode == 'synf':
        syn_flooding()
    elif mode == 'rst-com':
        communicate()
    elif mode == 'syn-com':
        try_start()
    else:
        print('Unknown attack {}'.format(mode))
