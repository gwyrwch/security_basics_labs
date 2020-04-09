import random
import socket
import time
import config1
from util import *


class Server:
    def __init__(self, port, is_daemon):
        # for TCP empty constructor or socket family = socket.AF_INET and socket type = socket.SOCK_DGRAM
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = config1.IP
        self.s.bind((config1.IP, port))
        self.is_daemon = is_daemon
        self.port = port
        self.hop_sessions = 0
        # self.syn_received_from = set()
        self.syn_queue = list()
        self.QUEUE_SIZE = 16

    def pos_in_queue(self, ip, port):
        for i in range(len(self.syn_queue)):
            if (ip, port) == (self.syn_queue[i][0], self.syn_queue[i][1]):
                return i
        return -1

    def get_msg(self):
        while True:
            msg, address = self.s.recvfrom(config1.buffer_size)
            msg = msg.decode()

            m = parse_tcp_ip_message(msg)

            if not tcp_ip_checks(m, self.IP):
                continue
            print(m)

            seq = int(m['sequence_number'], 2)
            ack = int(m['acknowledgment_number'], 2)
            if ack == 0:
                ack = random.randint(0, 2 ** 32 - 1)

            seq += 1
            seq %= 2 ** 32
            seq, ack = ack, seq
            seq = tobin(seq, 32)
            ack = tobin(ack, 32)

            if m['syn'] == '1':
                print(address)
                # passive scan and syn flooding
                if self.is_daemon:
                    # syn/ack
                    print('answer syn/ack')
                    tcp_msg = build_tcp_message(self.port, m['port_from'], syn='1', ack='1',
                                                sequence_number=seq, acknowledgment_number=ack)
                    ip_msg = build_ip_message(ip_from=self.IP, ip_to=m['ip_from'], data=tcp_msg)
                    print(m['ip_from'], m['port_from'], address)

                    if len(self.syn_queue):
                        print(self.syn_queue[0][2], time.time())

                    while len(self.syn_queue) and time.time() - self.syn_queue[0][2] > 7:
                        self.syn_queue = self.syn_queue[1:]

                    if self.pos_in_queue(m['ip_from'], m['port_from']) == -1:
                        if len(self.syn_queue) == self.QUEUE_SIZE:
                            pass
                        else:
                            self.s.sendto(ip_msg.encode(), (m['ip_from'], m['port_from']))
                            self.syn_queue.append((m['ip_from'], m['port_from'], time.time()))

                    print('Half-open sessions = {}'.format(len(self.syn_queue)))
                    time.sleep(0.5)
                else:
                    # rst
                    print('answer rst')
                    tcp_msg = build_tcp_message(self.port, m['port_from'], rst='1')
                    ip_msg = build_ip_message(ip_from=self.IP, ip_to=m['ip_from'], data=tcp_msg)
                    self.s.sendto(ip_msg.encode(), (m['ip_from'], m['port_from']))

                    pos = self.pos_in_queue(m['ip_from'], m['port_from'])
                    if pos != -1:
                        self.syn_queue.pop(pos)
            elif m['rst'] == '1':
                # tsp reset
                print('closing connection with', m['ip_from'], m['port_from'])

                pos = self.pos_in_queue(m['ip_from'], m['port_from'])
                if pos != -1:
                    self.syn_queue.pop(pos)

                tcp_msg = build_tcp_message(self.port, m['port_from'], rst='1')
                ip_msg = build_ip_message(ip_from=self.IP, ip_to=m['ip_from'], data=tcp_msg)
                self.s.sendto(ip_msg.encode(), (m['ip_from'], m['port_from']))
            elif m['ack'] == '1':
                pos = self.pos_in_queue(m['ip_from'], m['port_from'])
                if pos != -1:
                    self.syn_queue.pop(pos)

                print('Connection established')
            else:
                print(m['data'])
                tcp_msg = build_tcp_message(self.port, m['port_from'], data=m['data'],
                                            sequence_number=seq, acknowledgment_number=ack)
                ip_msg = build_ip_message(ip_from=self.IP, ip_to=m['ip_from'], data=tcp_msg)
                self.s.sendto(ip_msg.encode(), (m['ip_from'], m['port_from']))


if __name__ == '__main__':
    # server = Server()
    # server.get_msg()

    _port = input('what port to setup?\n')
    _is_daemon = input('am i daemon? y/N\n').lower() == 'y'
    server = Server(int(_port), _is_daemon)
    print('Server started on port {}'.format(_port))
    server.get_msg()
