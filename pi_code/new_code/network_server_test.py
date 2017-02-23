import socket
import json


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 6535))

print "Testen von 'player_join' (farbe: 255, 0, 0 name: 'olel')"

request = {'method': 'player_join', 'args': [[255, 0, 0], 'olel']}
request_json = json.dumps(request)
sock.send(request_json)
recv_json = json.loads(sock.recv(1024))

status = recv_json['status']
player_id = recv_json['player_id']
key = recv_json['key']
health = recv_json['health']

print "Antwort:\n\tStatus %d\n\tId %d\n\tHealth %d\n\tKey %s" % (status, player_id, health, key)

for i in range(0, 2):
    print "Testen von 'player_hit' (getroffen von sich selbst, %s schaden)" % ((i + 1) * 25)

    request = {'method': 'player_hit', 'args': [player_id, player_id, key, (i + 1) * 25]}
    request_json = json.dumps(request)
    sock.send(request_json)
    recv_json = json.loads(sock.recv(1024))

    status = recv_json['status']
    health = recv_json['health']
    hit_by = recv_json['name']

    print "Antwort:\n\tStatus %d\n\tHealth: %d\n\tName: %s" % (status, health, hit_by)


print "Testen von 'get_gameinfo'"

request = {'method': 'get_gameinfo', 'args': [player_id, key]}
request_json = json.dumps(request)
sock.send(request_json)
recv = sock.recv(65535)
recv_json = json.loads(recv)

status = recv_json['status']
health = recv_json['player_health']
game_time = recv_json['game_time']
active_players = recv_json['active_players']

print "Antwort:\n\tStatus %d\n\tHealth %d\n\tGame Time %f\n\tActive Players: %s" % (status, health, game_time, '\n\t'.join(map(str, active_players)))

print "Testen von 'player_quit'"

request = {'method': 'player_quit', 'args': [player_id, key]}
request_json = json.dumps(request)
sock.send(request_json)
recv_json = json.loads(sock.recv(1024))

print "Antwort:\n\tStatus %s" % recv_json['status']

sock.send("close")
sock.close()