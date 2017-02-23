import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 6535))

request = {'method': 'player_join',
           'args': [[255, 0, 0], 'olel']}

sock.send(request)

print sock.recv(1024)