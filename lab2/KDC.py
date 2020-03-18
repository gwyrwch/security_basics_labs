import socket
import time
from random import randint
from threading import Thread
import config
import json
from DES import DES
import random
import string

TGS_KEY = 'DV4GTMY'
SERVER_KEY = 'DCLM38S'


class ASServer:
    def __init__(self, show_bin=False):
        # for TCP empty constructor or socket family = socket.AF_INET and socket type = socket.SOCK_DGRAM
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((config.IP, config.AS_PORT))

        self.des = DES()

        self.all_uid_and_hashes = dict()
        self.session_bin_key = ''
        self.show_bin = show_bin
        with open('password_hashes.json', 'r') as f:
            self.all_uid_and_hashes = json.load(f)

    def get_and_send(self):
        while True:
            json_data, address = self.s.recvfrom(config.buffer_size)  # receive data from client
            data = dict()
            if json_data and address:
                data = json.loads(json_data.decode('utf-8'))
                # print(address, data)
            else:
                continue
            if data['query'] == 'first_time_package':
                uid = data['uid']
                enc_ts = data['ts']
                attempt = data['attempt']

                if uid not in self.all_uid_and_hashes:
                    ans_package = {
                        'query': 'no_such_user',
                        'msg': 'no user with such username',
                    }
                    self.s.sendto(str.encode(json.dumps(ans_package)), address)
                    continue

                uid_key = config.string_to_bin_list(self.all_uid_and_hashes[uid])

                try:
                    dec_ts = int(config.bin_list_to_string(self.des.decrypt(enc_ts, uid_key)))
                    if self.show_bin:
                        print("GET " + "['query': 'first_time_package', "
                              "'ts': {}, 'uid': {}, 'attempt': {}]".format(enc_ts, uid, attempt))
                    else:
                        print("GET " + "['query': 'first_time_package', "
                                       "'ts': {}, 'uid': {}, 'attempt': {}]".format(dec_ts, uid, attempt))
                except RuntimeError:
                    ans_package = {
                        'query': 'hacking_attempt',
                        'msg': 'invalid password',
                        'attempt': attempt
                    }

                    self.s.sendto(str.encode(json.dumps(ans_package)), address)
                    continue
                except ValueError:
                    ans_package = {
                        'query': 'hacking_attempt',
                        'msg': 'you are not {}'.format(uid),
                        'attempt': attempt
                    }

                    self.s.sendto(str.encode(json.dumps(ans_package)), address)
                    continue

                if dec_ts and time.time() - dec_ts > 300:
                    ans_package = {
                        'query': 'hacking_attempt',
                        'msg': 'you are not {}'.format(uid)
                    }
                    self.s.sendto(str.encode(json.dumps(ans_package)), address)
                    continue

                session_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
                self.session_bin_key = config.string_to_bin_list(session_key)
                ts = int(time.time())
                exp_ts = ts + 28800
                ans = {
                    'session_key': self.session_bin_key,
                    'ts': ts,
                    'exp_ts': exp_ts,
                    'TGS_addr': (config.IP, config.TGS_PORT)
                }
                enc_ans = self.des.encrypt(config.json_to_bin_list(ans), uid_key)

                # part with tgt
                tgt = {
                    'uid': uid,
                    'ts': ts,
                    'session_key': self.session_bin_key,
                    'exp_ts': exp_ts
                }
                enc_tgt = self.des.encrypt(config.json_to_bin_list(tgt), config.string_to_bin_list(TGS_KEY))

                ans_package = {
                    'query': 'first_time_and_tgt_package',
                    'first_time_json_enc': enc_ans,
                    'tgt_json_enc': enc_tgt
                }

                if self.show_bin:
                    print("SEND session_key " +
                          "['session_key': {},"
                          "'ts': {},"
                          "'exp_ts': {},"
                          "'TGS_addr': {}]\n".format(self.session_bin_key, ts, exp_ts, (config.IP, config.TGS_PORT)) +
                          "SEND TGT "
                          "['uid': {},"
                          "'ts': {},"
                          "'session_key': {},"
                          "'exp_ts': {}]".format(uid, ts, session_key, exp_ts))
                else:
                    print("SEND session_key " +
                          "['session_key': {},"
                          "'ts': {},"
                          "'exp_ts': {},"
                          "'TGS_addr': {}]\n".format(session_key, ts, exp_ts, [config.IP, config.TGS_PORT]) +
                          "SEND TGT " +
                          "['uid': {},"
                          "'ts': {},"
                          "'session_key': {},"
                          "'exp_ts': {}]".format(uid, ts, session_key, exp_ts))

                self.s.sendto(str.encode(json.dumps(ans_package)), address)


class TGSServer:
    def __init__(self, show_bin=False):
        # for TCP empty constructor or socket family = socket.AF_INET and socket type = socket.SOCK_DGRAM
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((config.IP, config.TGS_PORT))

        self.addresses = set()
        self.groups = {'all': []}
        self.user_times = dict()
        self.show_bin = show_bin

        self.des = DES()

    def get_and_send(self):
        while True:
            json_data, address = self.s.recvfrom(config.buffer_size)  # receive data from client
            data = dict()
            if json_data and address:
                data = json.loads(json_data.decode('utf-8'))
                # print(address, data)
            else:
                continue
            if data['query'] == 'tgs_request':
                tgt_data = json.loads(config.bin_list_to_string(
                    self.des.decrypt(
                        data['tgt_package'],
                        config.string_to_bin_list(TGS_KEY)
                    )
                ))

                session_key = tgt_data['session_key']
                user_data = json.loads(config.bin_list_to_string(
                    self.des.decrypt(
                        data['my_package'],
                        session_key
                    )
                ))
                if self.show_bin:
                    print("GET TGT " +
                          "['uid': {},"
                          "'ts': {},"
                          "'session_key': {},"
                          "'exp_ts': {}]".format(tgt_data['uid'], tgt_data['ts'], session_key, tgt_data['exp_ts']))
                else:
                    print(
                        "GET TGT " +
                        "['uid': {},"
                        "'ts': {},"
                        "'session_key': {},"
                        "'exp_ts': {}]".format(
                            tgt_data['uid'],
                            tgt_data['ts'],
                            config.bin_list_to_string(session_key),
                            tgt_data['exp_ts']
                        )
                    )

                if tgt_data['uid'] != user_data['uid']:
                    raise RuntimeError("uid of the tgt package and user package don't match")

                key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
                app_session_key = config.string_to_bin_list(
                    key
                )

                app_ans = {
                    'uid': user_data['uid'],
                    'address': address,
                    'ts': tgt_data['ts'],
                    'exp_ts': tgt_data['exp_ts'],
                    'app_session_key': app_session_key
                }
                user_ans = {
                    'dest': 'APP1',
                    'ts': tgt_data['ts'],
                    'exp_ts': tgt_data['exp_ts'],
                    'app_session_key': app_session_key
                }

                if self.show_bin:
                    print("SEND "
                          "['uid': {},"
                          "'address': {},"
                          "'ts': {},"
                          "'exp_ts': {}, "
                          "app_session_key]\n".format(
                              user_data['uid'], address, tgt_data['ts'], tgt_data['exp_ts'], app_session_key
                          ) +
                          "SEND  "
                          "['dest': APP1,"
                          "'ts': {},"
                          "'exp_ts': {}"
                          "'app_session_key': {}]".format(tgt_data['ts'], tgt_data['exp_ts'], app_session_key))
                else:
                    print("SEND "
                          "['uid': {},"
                          "'address': {},"
                          "'ts': {},"
                          "'exp_ts': {}, "
                          "app_session_key]\n".format(
                              user_data['uid'], address, tgt_data['ts'], tgt_data['exp_ts'], key) +
                          "SEND  "
                          "['dest': APP1,"
                          "'ts': {},"
                          "'exp_ts': {}, "
                          "'app_session_key': {}]".format(tgt_data['ts'], tgt_data['exp_ts'], key))

                ans = {
                    'query': 'tgt_response',
                    'user_package': self.des.encrypt(config.json_to_bin_list(user_ans), session_key),
                    'app_package': self.des.encrypt(
                        config.json_to_bin_list(app_ans), config.string_to_bin_list(SERVER_KEY)
                    )
                }
                self.s.sendto(str.encode(json.dumps(ans)), address)


if __name__ == '__main__':
    tgs_server = TGSServer()
    as_server = ASServer()

    thread_tgs = Thread(target=tgs_server.get_and_send)
    thread_as = Thread(target=as_server.get_and_send)

    thread_tgs.start()
    thread_as.start()
