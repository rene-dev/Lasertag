#!/usr/bin/env python

import socket
import sys
import select

class NetworkClient:
    def connect(self, ip, port, name):
        print "opening socket..."
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "connecting..."
        self.s.connect((ip, port))
        print "sending name: ", name
        self.s.send(name + "\n")
        self.playerid = None

    def disconnect(self):
        self.s.send("exit\n")
        print "closing socket..."
        self.s.close()

    def getPlayerId(self):
        return self.playerid

    def sendHitEvent(self, sourcePlayerId):
        print "sending: hit " + str(sourcePlayerId)
        self.s.send("hit " + str(sourcePlayerId) + "\n")

    def poll(self):
        try:
            self.s.setblocking(0) # don't block while receiving
	    data = self.s.recv(1024)
	    print "received data:", data
	    if self.playerid == None: # TODO: state machine or protocol?
	        self.playerid = int(data)
        except(socket.error):
	    pass # nothing received
        self.s.setblocking(1)


# tests
def keyPressed():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return True
    return False

if __name__ == '__main__':
    name = raw_input("name: ")

    client = NetworkClient()
    client.connect('127.0.0.1', 1234, name)
    while True:
        client.poll()
        if keyPressed():
            client.sendHitEvent(client.getPlayerId()) # hit self
