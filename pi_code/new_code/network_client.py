import socket
import json
import time

class NetworkException(Exception):
    pass

class NetworkClient(object):

    def __init__(self, name, color, ip, port=6535, ipv=socket.AF_INET):

        self.name = name
        self.color = color

        self.ipv = ipv
        self.ip = ip
        self.port = port

        self.sock = socket.socket(ipv, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))

        self.player_id = 0
        self.health = 0
        self.active_players = []
        self.damage_history = []
        self.game_time = 0
        self.key = ""

    def request(self, method, args):
        request = json.dumps({
            'method': method,
            'args': args
        })

        print request

        self.sock.send(request)

        j = None
        try:
            j = json.loads(self.sock.recv(1024))
        except:
            pass

        return j

    def join_game(self):

        response = self.request('player_join', {'color': list(self.color), 'name': self.name})

        if response['status'] == 0:
            self.player_id = response['player_id']
            self.health = response['health']
            self.key = response['key']
            return True
        else:
            raise NetworkException(response['message'])

    def quit_game(self):

        response = self.request('player_quit', {'player_id': self.player_id, 'key': self.key})

        if response['status'] == 0:
            self.request('close', {})
            self.sock.close()
            return True
        else:
            raise NetworkException(response['message'])

    def hit(self, opposite_id, damage):
        response = self.request('player_hit',
                                {'player_id': self.player_id, 'key': self.key, 'opposite_id': opposite_id, 'damage': damage})
        if response['status'] == 0:
            self.health = response['health']
            return response['name']
        else:
            raise NetworkException(response['message'])

    def get_gameinfo(self):

        response = self.request('get_gameinfo', {'player_id': self.player_id, 'key': self.key})

        if response['status'] == 0:
            self.health = response['player_health']
            self.active_players = response['active_players']
            self.game_time = response['game_time']
            self.damage_history = response['damage_history']
            return True
        else:
            raise NetworkException(response['message'])



if __name__ == "__main__":
    client = NetworkClient('olel', [255, 0, 127], 'localhost')
    client.join_game()
    client.get_gameinfo()

    print 'Status:'
    print '\tplayer_id:', client.player_id
    print '\tkey', client.key
    print '\thealth', client.health
    print '\tcolor', client.color
    print '\tgame_time', client.game_time
    print '\tactive_players', client.active_players
    print '\tdamage_history', client.damage_history

    while 1:
        try:
            client.get_gameinfo()

            print 'Status:'
            print '\tplayer_id:', client.player_id
            print '\tkey', client.key
            print '\thealth', client.health
            print '\tcolor', client.color
            print '\tgame_time', client.game_time
            print '\tactive_players', client.active_players
            print '\tdamage_history', client.damage_history
            time.sleep(0.25)
        except KeyboardInterrupt:
            break

    client.quit_game()