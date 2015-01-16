#!/usr/bin/python
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class Player(LineReceiver):
    def __init__(self, factory):		#constructor
        self.factory = factory			#pointer auf PlayerFactory
        self.name = None
        self.state = "name"
        self.delimiter = "\n"
        self.playerid = 0

    def connectionLost(self, reason):
        if self.playerid in self.factory.users:
            del self.factory.users[self.playerid]

    def lineReceived(self, line):		#zeile wird empfangen
        if line == "exit":
            self.transport.loseConnection()
            return
        if self.state == "name":		#erste zeile nach player connect beinhaltet seinen namen
            self.handle_name(line)
        else:							#irgendwas wird empfangen
            self.handle(line)

    def handle_name(self, name):		#name des neuen players empfangen
        if name in self.factory.users or name == "":
            self.sendLine("error name in use")
            return
        self.playerid = self.factory.get_playerid()	#neue playerid generieren
        self.sendLine(str(self.playerid))			#playerid an client senden
        self.name = name
        self.factory.users[self.playerid] = self	#pointer auf den player im dictionary (array) in PlayerFactory speichern
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

class PlayerFactory(Factory):		#gibts nur ein mal, verwaltet alle player
    def __init__(self):
        self.users = {}
        self.playerid = 0

    def buildProtocol(self, addr):	#on every player connect
        return Player(self)			#make new instance of Player, PlayerFactory übergibt sich selbst an Player

    def get_playerid(self):			#playerid für neuen player generieren
        self.playerid += 1
        return self.playerid

reactor.listenTCP(1234, PlayerFactory())
reactor.run()