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
    def __init__(self, player_id, key):
        self.player_id = player_id
        self.key = key

        self.properties = {}

    def set_property(self, prop, value):
        if not prop in self.properties.keys():
            self.properties.update({prop: value})
        else:
            self.properties[prop] = value

    def get_property(self, prop):
        if prop in self.properties.keys():
            return self.properties[prop]
        else:
            return None


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
                elif method == 'get_property':
                    ret = self.server.get_property(args)
                elif method == 'set_property':
                    ret = self.server.set_property(args)
                elif method == "close":
                    self.running = False
                    ret = {'status': 0}

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
            if connection.running:
                connection.shutdown()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def player_join(self, args):

        player_id = len(self.players)
        num = random.randint(0, 2 ** 16)  # Max 65536 spieler sollte reichen
        while num in self.used_hashes:
            num = random.randint(0, 2 ** 16)
        _hash = hashlib.sha512()  # Ein bisschen overpowered, aber sicher ist sicher ;D
        _hash.update(str(num))
        key = _hash.hexdigest()

        player = Player(player_id, key)
        self.players.append(player)

        dic = {'player_id': player_id,
               'key': key,
               'status': 0}

        if self.start_time == 0:  # Spiel hat noch nicht gestartet, oder es ist der 01.01.1970
            self.start_time = time.time()

        return dic

    def player_quit(self, args):
        player_id = args['player_id']
        key = args['key']

        dic = {'status': 0} if key == self.players[player_id].key else {'status': 1, 'message': 'ACCESS DENIED'}

        if key == self.players[player_id].key:
            self.players[player_id].active = False

        return dic

    def set_property(self, args):
        player_id = args['player_id']
        key = args['key']
        prop = args['property']
        val = args['value']

        if key == self.players[player_id].key:
            self.players[player_id].set_property(prop, val)
            dic = {'status': 0}
        else:
            dic = {'status': 1, 'message': 'ACCESS DENIED'}
        return dic

    def get_property(self, args):
        player_id = args['player_id']
        key = args['key']
        prop = args['property']

        if key == self.players[player_id].key:
            val = self.players[player_id].get_property(prop)
            dic = {'status': 0, 'value': val}
        else:
            dic = {'status': 1, 'message': 'ACCESS DENIED'}

        return dic


if __name__ == "__main__":
    server = NetworkServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print "Received KeyboardInterrupt, shutting down!"
        server.shutdown()
