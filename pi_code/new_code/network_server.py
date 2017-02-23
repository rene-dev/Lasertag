# -*- coding:utf-8 -*-
#
# Autoren:
#   OleL
#

import socket
import time
import hashlib, random  # To generate hash
import threading
import json

class Player(object):
    def __init__(self, player_id, color, name, key, health=100):
        self.player_id = player_id
        self.color = color
        self.key = key
        self.name = name

        self.health = health
        self.damage_history = []

    def hit(self, player_id, damage):
        self.damage_history.append({'time': time.time(), 'hit_by': player_id, 'damage': damage, 'health': self.health})


class ClientThread(threading.Thread):

    def __init__(self, conn, addr, server):

        super(ClientThread, self).__init__()
        self.daemon = True

        self.conn = conn
        self.addr = addr
        self.server = server

    def run(self):
        while 1:
            input = self.conn.recv(1024)
            dic = json.loads(input)

            method = dic['method']
            args = dic['args']

            if method == 'player_join':
                ret = self.server.player_join(args)
            elif method == 'player_quit':
                ret = self.server.player_quit(args)
            elif method == 'player_hit':
                ret = self.server.player_hit(args)
            elif method == 'get_gameinfo':
                ret = self.server.get_gameinfo(args)
            else:
                ret = {'status': 1, 'message': 'METHOD NOT FOUND'}

            j = json.dumps(ret)

            self.conn.send(j)

class NetworkServer(object):
    def __init__(self):
        self.players = []
        self.used_hashes = []

        self.start_time = 0

        self.port = 6535  # Port used for all network communication

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.port))

        self.connections = []

    def run(self):

        self.sock.listen(5)

        while 1:
            connection, address = self.sock.accept()
            client = ClientThread(connection, address, self)
            client.start()
            self.connections.append(client)

    def player_join(self, args):
        color = args[0]
        name = args[1]

        player_id = len(self.players)
        num = random.randint(0, 2 ** 16)  # Max 65536 spieler sollte reichen
        while num in self.used_hashes:
            num = random.randint(0, 2 ** 16)
        _hash = hashlib.sha512()  # Ein bisschen overpowered, aber sicher ist sicher ;D
        _hash.update(num)
        key = _hash.hexdigest()

        player = Player(player_id, color, name, key)
        self.players.append(player)

        dic = {'player_id': player_id,
               'health': player.health,
               'key': key,
               'status': 0}

        if self.start_time == 0:  # Spiel hat noch nicht gestartet, oder es ist der 01.01.1970
            self.start_time = time.time()

        return dic

    def player_hit(self, args):
        player_id = args[0]  # ID des beschossenen spielers
        opposit_id = args[1]  # ID des schießenden spielers
        key = args[2]  # Key für Authentifizierung
        damage = args[3]  # Zugefügter schaden

        if key == self.players[player_id].key:
            self.players[player_id].hit(opposit_id, damage)

        dic = {'health': self.players[player_id].health,
               'name': self.players[opposit_id].name,
               'status': 0}

        return dic if key == self.players[player_id].key else {'status': 1, 'message': 'ACCESS DENIED'}

    def player_quit(self, args):
        player_id = args[0]
        key = args[1]

        if key == self.players[player_id].key:
            self.players.pop(self.players[player_id])

        return {'status': True} if key == self.players[player_id].key else{'status': 1, 'message': 'ACCESS DENIED'}

    def get_gameinfo(self, args):
        player_id = args[0]
        key = args[1]

        active_players = []
        for player in self.players:
            active_players.append({'player_id': player.player_id, 'player_name': player.name})

        player = self.players[player_id]

        dic = {'active_players': active_players,
               'player_health': player.health,
               'game_time': time.time() - self.start_time,
               'status': 0}

        return dic if key == self.players[player_id].key else {'status': 1, 'message': 'ACCESS DENIED'}

if __name__ == "__main__":
    NetworkServer().run()