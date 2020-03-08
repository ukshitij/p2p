import socket
import threading
import sys
import random
import time

class Client:
	ip = ""
	hostip = ""
	userid = ""
	peers = []
	connections = []
	sock = None
	sThread = None
	rThread = None
	hmThread = None

	def __init__(self, address, uname):
		self.ip = socket.gethostbyname(socket.gethostname())
		self.userid = uname
		self.hostip = address

		if self.ip != self.hostip: 
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.connect((address, 10000))

			self.sock.send(bytes(self.userid + "(" + self.ip + ") is connected."))

			self.sThread = threading.Thread(target=self.sendMsg, args=(self.sock,), name='send')
			self.sThread.daemon = True
			self.sThread.start()

			self.rThread = threading.Thread(target=self.recvMsg, args=(self.sock,), name='recv')
			self.rThread.daemon = True
			self.rThread.start()

		else:
			self.peers.append(self.ip)
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind(('0.0.0.0', 10000))
			self.sock.listen(1)
			print("Chat room hosted. Host-IP : " + self.ip)

			self.hmThread = threading.Thread(target=self.hostMsg, args=())
			self.hmThread.daemon = True
			self.hmThread.start()

			while True:
				try:
					c, a = self.sock.accept()
					self.connections.append(c)
					self.peers.append(a[0])

					hThread = threading.Thread(target=self.handler, args=(c, a))
					hThread.daemon = True
					hThread.start()

					self.sendPeers()

				except (KeyboardInterrupt, EOFError) as e:
					self.peers.remove(self.ip)
					newHost = random.choice(self.peers)
					for connection in self.connections:
						connection.send(b'\x10' + bytes(newHost, 'utf-8'))
					sys.exit(0)
					##############################

	def becomeHost():
		self.peers.append(self.ip)
		self.sock.close()

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('0.0.0.0', 10000))
		self.sock.listen(1)
		print("Chat room hosted. Host-IP : " + self.ip)

		self.hmThread = threading.Thread(target=self.hostMsg, args=())
		self.hmThread.daemon = True
		self.hmThread.start()

		while True:
			try:
				c, a = self.sock.accept()
				self.connections.append(c)
				self.peers.append(a[0])

				hThread = threading.Thread(target=self.handler, args=(c, a))
				hThread.daemon = True
				hThread.start()

				self.sendPeers()
			except (KeyboardInterrupt, EOFError) as e:
				self.peers.remove(ip)
				newHost = random.choice(self.peers)
				for connection in self.connections:
					connection.send(b'\x10' + bytes(newHost, 'utf-8'))
				sys.exit(0)

	def reconnect(self, newip):
		self.sThread.exit()
		self.rThread.exit()
		self.hostip = newip
		self.peers = []
		self.connections = []

		if self.ip == newip:
			becomeHost()
		else:
			time.sleep(3)
			self.sock.connect((newip, 10000))

			self.sock.send(bytes(self.userid + "(" + self.ip + ") is connected."))

			self.sThread = threading.Thread(target=self.sendMsg, args=(self.sock,), name='send')
			self.sThread.daemon = True
			self.sThread.start()

			self.rThread = threading.Thread(target=self.recvMsg, args=(self.sock,), name='recv')
			self.rThread.daemon = True
			self.rThread.start()

	def hostMsg(self):
		while True:
			m = self.userid + "(" + self.ip + ")" + ":" + input("")
			print(m)
			for connection in self.connections:
				connection.send(bytes(m, 'utf-8'))

	def sendPeers(self):
		p = ""
		for peer in self.peers:
			p = p + peer + ","
		for connection in self.connections:
			connection.send(b'\x11' + bytes(p, 'utf-8'))

	def handler(self, c, a):
		while True:
			data = c.recv(1024)
			if not data:
				disMsg = str(a[0]) + ':' + str(a[1]) + " has disconnected."
				print(disMsg)
				self.connections.remove(c)
				self.peers.remove(a[0])
				c.close()
				for connection in self.connections:
					connection.send(bytes(disMsg, 'utf-8'))	
				self.sendPeers()
				break

			for connection in self.connections:
				connection.send(data)
			print(str(data, 'utf-8'))


	def sendMsg(self, sock):
		while True:
			sock.send(bytes(self.userid + "(" + self.ip + ")" + ":" + input(""), 'utf-8'))

	def recvMsg(self, sock):
		while True:
			data = sock.recv(1024)
			if not data:
				break
			if data[0:1] == b'\x10':
				self.reconnect(str(data[1:], 'utf-8'))
			elif data[0:1] == b'\x11':
				self.updatePeers(data[1:])
			else:
				print(str(data, 'utf-8'))
	
	def updatePeers(self, peerData):
		self.peers = str(peerData, 'utf-8').split(',')


global client

def main():
	print("Choose one of the following:")
	print("1. To join a chat room.")
	print("2. To create a chat room.")

	c = input()
	un = ""
	hip = ""
	if c == '1':
		print("enter username and host-IP")
		un = input()
		hip = input()
		check = 1
		while check == 1:
			try:
				client = Client(hip, un)
			except (KeyboardInterrupt, EOFError) as e:
				check = 0
				sys.exit(0)
			except:
				print("!could not connect! retrying ...")
				time.sleep(3)

	elif c == '2':
		print("enter username")
		un = input()
		hip = socket.gethostbyname(socket.gethostname())
		client = Client(hip, un)

	else:
		print("invalid input. exiting ...")
		sys.exit(0)


if __name__ == "__main__":
	main()