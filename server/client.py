#!/usr/bin/env python

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 1234

print "open socket..."
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "connecting..."
s.connect((TCP_IP, TCP_PORT))

name = raw_input("name: ")
print "sending name: ", name
s.setblocking(0)
s.send(name + "\n")
s.setblocking(1)

print "recieving data..."
data = s.recv()
print "received data:", data

print "closing socket..."
s.close()