import socket
import json
import time

class NetworkException(Exception):
    pass

class NetworkClient(object):

    def __init__(self, ip, port=6535, ipv=socket.AF_INET):

        self.ipv = ipv
        self.ip = ip
        self.port = port

        self.sock = socket.socket(ipv, socket.SOCK_STREAM)

        self.player_id = 0
        self.key = ""

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))

    def disconnect(self):
        self.request('close', {})
        self.sock.close()

    def request(self, method, args):
        request = json.dumps({
            'method': method,
            'args': args
        })

        self.sock.send(request)

        j = None
        try:
            j = json.loads(self.sock.recv(1024))
        except:
            pass

        return j

    def join_game(self):

        response = self.request('player_join', {})

        if response['status'] == 0:
            self.player_id = response['player_id']
            self.key = response['key']
            return True
        else:
            raise NetworkException(response['message'])

    def quit_game(self):

        response = self.request('player_quit', {'player_id': self.player_id, 'key': self.key})

        if response['status'] == 0:
            return True
        else:
            raise NetworkException(response['message'])

    def get_property(self, prop):

        response = self.request('get_property', {'player_id': self.player_id, 'key': self.key, 'property': prop})

        if response['status'] == 0:
            return response['value']
        else:
            raise NetworkException(response['message'])

    def set_property(self, prop, val):

        response = self.request('set_property', {'player_id': self.player_id, 'key': self.key, 'property': prop, 'value': val})

        if response['status'] == 0:
            return True
        else:
            raise NetworkException(response['message'])

if __name__ == "__main__":
    client = NetworkClient('localhost')
    client.connect()

    client.join_game()

    client.set_property('test', '1234')
    client.set_property('abcd', '4321')

    print client.get_property('abcd')
    print client.get_property('test')

    client.quit_game()

    client.disconnect()