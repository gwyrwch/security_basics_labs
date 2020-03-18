import socket
import time
from random import randint
from threading import Thread
import config
import json

from DES import DES


class Server:
    def __init__(self, show_bin=False):
        # for TCP empty constructor or socket family = socket.AF_INET and socket type = socket.SOCK_DGRAM
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((config.IP, config.SERVER_PORT))
        self.KEY = 'DCLM38S'

        self.des = DES()
        self.show_bin = show_bin

    def get_msg(self):
        while True:
            msg, address = self.s.recvfrom(config.buffer_size)
            data = json.loads(msg.decode('utf-8'))
            # print(data)

            if data['query'] == 'user_request':
                app_package = json.loads(config.bin_list_to_string(
                    self.des.decrypt(data['app_package'], config.string_to_bin_list(self.KEY))
                ))
                print("GET app_package" +
                      "['uid': {},"
                      "'address': {},"
                      "'ts': {},"
                      "'exp_ts': {}, "
                      "app_session_key]".format(
                          app_package['uid'], app_package['address'], app_package['ts'],
                          app_package['exp_ts'], app_package['app_session_key'])
                      )

                user_package = json.loads(config.bin_list_to_string(
                    self.des.decrypt(data['user_package'], app_package['app_session_key'])
                ))
                print("GET user data" + "['uid': {}, 'ts': {}]\n".format(user_package['uid'], user_package['ts']))

                if user_package['uid'] != app_package['uid']:
                    raise RuntimeError("uid of the tgt package and user package don't match")

                print("SEND " + "['name': 'APP1', 'ts': {}]".format(str(int(time.time()))))
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
