import socket
import time
from random import randint
from threading import Thread
import config
import json
from util import *



class Server:
    def __init__(self, port, is_daemon):
        # for TCP empty constructor or socket family = socket.AF_INET and socket type = socket.SOCK_DGRAM
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = config.IP
        self.s.bind((config.IP, port))
        self.is_daemon = is_daemon
        self.port = port

    def get_msg(self):
        while True:
            msg, address = self.s.recvfrom(config.buffer_size)
            msg = msg.decode()
            print(address)
            m = parse_tcp_ip_message(msg)

            if not tcp_ip_checks(m, self.IP):
                continue

            if m['syn'] == '1' and m['ack'] == '1':
                if is_daemon:
                    # syn/ack
                    print('answer syn/ack')
                    tcp_msg = build_tcp_message(self.port, m['port_from'], syn='1', ack='1')
                    ip_msg = build_ip_message(ip_from=self.IP, ip_to=m['ip_from'], data=tcp_msg)
                    print(m['ip_from'], m['port_from'], address)
                    self.s.sendto(ip_msg.encode(), (m['ip_from'], m['port_from']))
                else:
                    # rst
                    print('answer rst')
                    tcp_msg = build_tcp_message(self.port, m['port_from'], rst='1')
                    ip_msg = build_ip_message(ip_from=self.IP, ip_to=m['ip_from'], data=tcp_msg)
                    self.s.sendto(ip_msg.encode(), (m['ip_from'], m['port_from']))



if __name__ == '__main__':
    # server = Server()
    # server.get_msg()

    port = input('what port to setup?\n')
    is_daemon = input('am i daemon? y/N\n').lower() == 'y'
    server = Server(int(port), is_daemon)
    server.get_msg()
