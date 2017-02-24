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
        self.active = True

    def hit(self, opposite_id, damage):
        self.damage_history.append({'time': time.time(), 'hit_by': opposite_id, 'damage': damage, 'health': self.health})

        self.health -= damage


class ClientThread(threading.Thread):

    def __init__(self, conn, addr, server):

        super(ClientThread, self).__init__()
        self.daemon = True

        self.conn = conn
        self.addr = addr
        self.server = server
        self.running = True

    def shutdown(self):
        self.conn.close()
        print "Closing connection from", self.addr

    def run(self):
        while self.running:
            input = self.conn.recv(1024)
            try:
                dic = json.loads(input)

                method = dic['method']
                args = dic['args']

                ret = {'status': 1, 'message': 'METHOD NOT FOUND'}

                if method == 'player_join':
                    ret = self.server.player_join(args)
                elif method == 'player_quit':
                    ret = self.server.player_quit(args)
                elif method == 'player_hit':
                    ret = self.server.player_hit(args)
                elif method == 'get_gameinfo':
                    ret = self.server.get_gameinfo(args)
                elif method == "close":
                    self.running = False

                j = json.dumps(ret)

                self.conn.send(j)
            except:
                pass
        self.shutdown()
        print "DONE", self.addr

class NetworkServer(object):
    def __init__(self):
        self.players = []
        self.used_hashes = []

        self.start_time = 0

        self.port = 6535  # Port used for all network communication

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(True)
        self.sock.bind(('0.0.0.0', self.port))

        self.connections = []

    def run(self):

        self.sock.listen(5)

        while 1:
            connection, address = self.sock.accept()
            print "New connection from", address
            client = ClientThread(connection, address, self)
            client.start()
            self.connections.append(client)

    def shutdown(self):
        for connection in self.connections:
            connection.shutdown()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def player_join(self, args):
        color = args['color']
        name = args['name']

        player_id = len(self.players)
        num = random.randint(0, 2 ** 16)  # Max 65536 spieler sollte reichen
        while num in self.used_hashes:
            num = random.randint(0, 2 ** 16)
        _hash = hashlib.sha512()  # Ein bisschen overpowered, aber sicher ist sicher ;D
        _hash.update(str(num))
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
        player_id = args['player_id']  # ID des beschossenen spielers
        opposite_id = args['opposite_id']  # ID des schießenden spielers
        key = args['key']  # Key für Authentifizierung
        damage = args['damage']  # Zugefügter schaden

        if key == self.players[player_id].key:
            self.players[player_id].hit(opposite_id, damage)

        dic = {'health': self.players[player_id].health,
               'name': self.players[opposite_id].name,
               'status': 0}

        return dic if key == self.players[player_id].key else {'status': 1, 'message': 'ACCESS DENIED'}

    def player_quit(self, args):
        player_id = args['player_id']
        key = args['key']

        dic = {'status': 0} if key == self.players[player_id].key else {'status': 1, 'message': 'ACCESS DENIED'}

        if key == self.players[player_id].key:
            self.players[player_id].active = False

        return dic

    def get_gameinfo(self, args):
        player_id = args['player_id']
        key = args['key']

        active_players = []
        for player in self.players:
            if player.active:
                active_players.append({'player_id': player.player_id, 'player_name': player.name})

        player = self.players[player_id]

        dic = {'active_players': active_players,
               'damage_history': player.damage_history,
               'player_health': player.health,
               'game_time': time.time() - self.start_time,
               'status': 0}

        return dic if key == self.players[player_id].key else {'status': 1, 'message': 'ACCESS DENIED'}

if __name__ == "__main__":
    server = NetworkServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print "Received KeyboardInterrupt, shutting down!"
        server.shutdown()
