import socket
import time
from random import randint
from threading import Thread
import config
import json

from DES import DES


class Server:
    def __init__(self):
        # for TCP empty constructor or socket family = socket.AF_INET and socket type = socket.SOCK_DGRAM
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((config.IP, config.SERVER_PORT))
        self.KEY = 'DCLM38S'

        self.des = DES()

    def get_msg(self):
        while True:
            msg, address = self.s.recvfrom(config.buffer_size)
            data = json.loads(msg.decode('utf-8'))
            print(data)

            if data['query'] == 'user_request':
                app_package = json.loads(config.bin_list_to_string(
                    self.des.decrypt(data['app_package'], config.string_to_bin_list(self.KEY))
                ))
                user_package = json.loads(config.bin_list_to_string(
                    self.des.decrypt(data['user_package'], app_package['app_session_key'])
                ))

                if user_package['uid'] != app_package['uid']:
                    raise RuntimeError("uid of the tgt package and user package don't match")

                app_response = {
                    'query': 'app_response',
                    'app_response': self.des.encrypt(
                        config.json_to_bin_list(
                            {
                                'name': 'APP1',
                                'ts': str(int(time.time()))
                            }
                        ), app_package['app_session_key']
                    )
                }
                self.s.sendto(str.encode(json.dumps(app_response)), address)


if __name__ == '__main__':
    server = Server()
    server.get_msg()
