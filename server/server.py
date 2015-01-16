#!/usr/bin/python
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class Player(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.state = "name"
        self.delimiter = "\n"
        self.playerid = 0

    def connectionLost(self, reason):
        if self.playerid in self.factory.users:
            del self.factory.users[self.playerid]

    def lineReceived(self, line):
        if line == "exit":
            self.transport.loseConnection()
            return
        if self.state == "name":
            self.handle_name(line)
        else:
            self.handle(line)

    def handle_name(self, name):
        if name in self.factory.users or name == "":
            self.sendLine("error name in use")
            return
        self.playerid = self.factory.get_playerid()
        self.sendLine(str(self.playerid))
        self.name = name
        self.factory.users[self.playerid] = self
        self.state = "joined"

    def handle(self, line):
        cmd = line.split(" ",1)
        if len(cmd) > 1 and cmd[0] == "hit":
            try:
                param = int(cmd[1])
                if self.factory.users.has_key(param):
                    self.sendLine("ok")
                    self.factory.users[param].sendLine("hitfrom " + self.name)
                else:
                    self.sendLine("error user not found")
            except ValueError:
                    self.sendLine("error")

class PlayerFactory(Factory):
    def __init__(self):
        self.users = {}
        self.playerid = 0

    def buildProtocol(self, addr):
        return Player(self)

    def get_playerid(self):
        self.playerid += 1
        return self.playerid

reactor.listenTCP(1234, PlayerFactory())
reactor.run()