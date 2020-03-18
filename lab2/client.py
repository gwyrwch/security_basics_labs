import socket
import time
import config
import json
from DES import DES
import hashlib


class Client:
    def __init__(self, show_bin=False):
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.des = DES()

        print('username: ', end=' ')
        self.name = input()
        print('password: ', end=' ')
        self.password = input()

        hash_ = hashlib.md5(self.password.encode())
        self.KEY = hash_.hexdigest()[:7]
        self.bin_key = config.string_to_bin_list(self.KEY)

        self.session_bin_key = None
        self.app_session_key = None
        self.TGT_package = None
        self.app_package = None
        self.show_bin = show_bin

        cur_time = str(int(time.time()))
        ts = config.string_to_bin_list(cur_time)

        package = {
            'query': 'first_time_package',
            'ts': self.des.encrypt(ts, self.bin_key),
            'uid': self.name,
            'attempt': 1
        }

        if show_bin:
            print(
                "SEND ['query': 'first_time_package',"
                "'ts': {},"
                "'uid':{},"
                "'attempt': 1]".format(self.des.encrypt(ts, self.bin_key), self.name)
            )
        else:
            print(
                "SEND ['query': 'first_time_package', 'ts': {}, 'uid': {}, 'attempt': 1]".format(cur_time, self.name)
            )

        self.s.sendto(str.encode(json.dumps(package)), (config.IP, config.AS_PORT))

    def get_msg(self):
        while True:
            msg, address = self.s.recvfrom(config.buffer_size)
            data = json.loads(msg.decode('utf-8'))
            # print(data)

            if data['query'] == 'first_time_and_tgt_package':
                enc_ans = data['first_time_json_enc']
                dec_ans = self.des.decrypt(enc_ans, self.bin_key)

                ans = json.loads(config.bin_list_to_string(dec_ans))
                self.session_bin_key = ans['session_key']
                tgs_address = ans['TGS_addr']

                self.TGT_package = data['tgt_json_enc']
                if self.show_bin:
                    print("GET session key {} and save TGT package".format(self.session_bin_key))
                else:
                    print("GET session key {} and save TGT package".format(
                        config.bin_list_to_string(self.session_bin_key))
                    )

                my_package = {
                    'uid': self.name,
                    'ts': ans['ts']
                }

                print(
                    "SEND ['uid': {}, 'ts': {}]".format(self.name, ans['ts']) + " and TGT package"
                )
                enc_my_package = self.des.encrypt(config.json_to_bin_list(my_package), self.session_bin_key)

                full_package = {
                    'query': 'tgs_request',
                    'my_package': enc_my_package,
                    'tgt_package': self.TGT_package
                }
                self.s.sendto(str.encode(json.dumps(full_package)), tuple(tgs_address))
            elif data['query'] == 'tgt_response':
                user_package = json.loads(config.bin_list_to_string(self.des.decrypt(data['user_package'], self.session_bin_key)))
                self.app_session_key = user_package['app_session_key']
                self.app_package = data['app_package']

                print("GET app_session_key and save app_package")

                package_to_app = {
                    'query': 'user_request',
                    'user_package': self.des.encrypt(config.json_to_bin_list({
                        'uid': self.name,
                        'ts': user_package['ts'],
                    }), self.app_session_key),
                    'app_package': self.app_package
                }

                print("SEND app_package and ['uid': {}, 'ts': {}]".format(self.name, user_package['ts']))

                self.s.sendto(str.encode(json.dumps(package_to_app)), (config.IP, config.SERVER_PORT))
            elif data['query'] == 'app_response':
                app_response = json.loads(config.bin_list_to_string(self.des.decrypt(data['app_response'], self.app_session_key)))
                print("GET response from app with name {}".format("APP1"))
                # print(app_response['name'], app_response['ts'])
                exit(0)
            elif data['query'] == 'hacking_attempt':
                # print(data['msg'])
                if data['attempt'] == 3:
                    print('it was last attempt')
                    exit(0)
                print('try again. attempt {}'.format(data['attempt']))
                print('password: ', end=' ')
                self.password = input()

                hash_ = hashlib.md5(self.password.encode())
                self.KEY = hash_.hexdigest()[:7]
                self.bin_key = config.string_to_bin_list(self.KEY)

                ts = config.string_to_bin_list(str(int(time.time())))

                package = {
                    'query': 'first_time_package',
                    'ts': self.des.encrypt(ts, self.bin_key),
                    'uid': self.name,
                    'attempt': data['attempt'] + 1
                }
                self.s.sendto(str.encode(json.dumps(package)), (config.IP, config.AS_PORT))
            elif data['query'] == 'no_such_user':
                print(data['msg'])
                exit(0)



if __name__ == '__main__':
    client = Client()
    client.get_msg()