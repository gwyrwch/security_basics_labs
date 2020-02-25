import socket
from lab3 import config
from lab3.util import *
import select


class Client:
    def __init__(self, my_port):
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.port = my_port
        self.IP = config.IP
        self.s.bind((config.IP, self.port))
        # self.s.setblocking(0)
        self.s.settimeout(0.5)

    def get_msg(self):
        try:
            msg, address = self.s.recvfrom(config.buffer_size)
        except Exception as e:
            print(e)
            return None

        return msg.decode()

    def send_to_port(self, port_to, **kwargs):
        tcp_msg = build_tcp_message(self.port, port_to, **kwargs)
        ip_msg = build_ip_message(ip_from=self.IP, ip_to=config.IP, data=tcp_msg)
        self.s.sendto(ip_msg.encode(), (config.IP, port_to))


def passive_scan():
    client = Client(22222)

    ccasks = 0
    misses = 0
    for port in range(20000, 20005):
        client.send_to_port(port, syn='1', ack='1')
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


if __name__ == '__main__':
    passive_scan()
