# network.py

import sys
import socket
import select
from uuid import getnode as get_mac

class Client_server:

	def __init__(self,host,port):
		self.mac = get_mac()
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.settimeout(2)
	 
		# connect to remote host
		try:
			self.s.connect((host, port))
		except:
			print 'Unable to connect'
			sys.exit()

	def send(self,msg):
		self.s.send("%12X: %s" % (self.mac, msg))

	def empf(self):
		self.s.socket_list = [sys.stdin, self.s]
		while 1:
			self.s.socket_list = [sys.stdin, self.s]
			ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
			for sock in ready_to_read:			 
				if sock == s:
					data = sock.recv(4096) 
					return data

if __name__ == "__main__":
	cs=Client_server("10.0.8.200", 9005)
	cs.send("test")
