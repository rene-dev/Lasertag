#!/usr/bin/python
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from enum import Enum

class ProtocolState(Enum):
	IDENTITY_EXCHANGE = 0
	JOINED = 1

class Player(LineReceiver):
    def __init__(self, factory):				#constructor
        print "client connected"
        self.factory = factory					#pointer auf PlayerFactory
        self.name = None
        self.state = ProtocolState.IDENTITY_EXCHANGE
        self.delimiter = "\n"
        self.playerid = 0

    def connectionLost(self, reason):
        if self.playerid in self.factory.users:
            print "client disconnected (", self.name, ",", self.playerid, ")"
            del self.factory.users[self.playerid]

    def lineReceived(self, line):				#zeile wird empfangen
        if line == "exit":
            self.transport.loseConnection()
            return
        if self.state == ProtocolState.IDENTITY_EXCHANGE:	#erste zeile nach player connect beinhaltet seinen namen
            self.handleIdentityExchange(line)
        else:							#irgendwas wird empfangen
            self.handle(line)

    def handleIdentityExchange(self, name):			#name des neuen players empfangen
        if name in self.factory.users or name == "":
            self.sendLine("error: name in use")
            return
        self.playerid = self.factory.createPlayerid()		#neue playerid generieren
        self.sendLine(str(self.playerid))			#playerid an client senden
        self.name = name
        self.factory.users[self.playerid] = self		#pointer auf den player im dictionary (array) in PlayerFactory speichern
        self.state = ProtocolState.JOINED
        print "player joined (", self.name, ",", self.playerid, ")"

    def handle(self, line):
        cmd = line.split(" ", 1)
        if len(cmd) > 1 and cmd[0] == "hit":
            try:
                param = int(cmd[1])
                if self.factory.users.has_key(param):
                    self.sendLine("ok")
                    self.factory.users[param].sendLine("hitfrom " + self.name) # ??? sollte das nicht andersrum sein? self wird doch von dem user in param getroffen, oder nicht?
                    print self.name, "was hit by", self.factory.users[param].name
                else:
                    self.sendLine("error: user not found")
            except ValueError:
                self.sendLine("error")

class PlayerFactory(Factory):					#gibts nur ein mal, verwaltet alle player
    def __init__(self):
        self.users = {}
        self.playerid = 0

    def buildProtocol(self, addr):				#on every player connect
        return Player(self)					#make new instance of Player, PlayerFactory ubergibt sich selbst an Player

    def createPlayerid(self):					#playerid fur neuen player generieren
        self.playerid += 1
        return self.playerid

if __name__ == '__main__':
    reactor.listenTCP(1234, PlayerFactory())
    while True:
        reactor.iterate()
        #print "iteration"
