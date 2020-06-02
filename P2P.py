import sys
import threading
import socket
import time
HOST = '127.0.0.1'
PORT_BIAS = 16000
DATA_SIZE = 1024
MAX_LOST_PACKET = 2
MAX_NODES = 256
class P2P():
	def __init__(self,name,firstSuccessor,secondSuccessor,pingInterval):
		self.name = name
		self.port = int(name) + PORT_BIAS
		self.firstSuccessor = int(firstSuccessor) + PORT_BIAS
		self.secondSuccessor = int(secondSuccessor) + PORT_BIAS
		self.pingInterval = int(pingInterval)
		self.firstSuccessorAlive = 0
		self.secondSuccessorAlive = 0
		self.preFirstSuccessor = None
		self.preSecondSuccessor = None
		self.udpServerState = True
		self.tcpServerState = True
		self.detecter = threading.Timer(self.pingInterval/5,self.check_successor)
		self.requestFile = None
	def udp_server_init(self):
		self.serverClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serverSocket.bind((HOST, self.port))
		self.recv_thread=threading.Thread(name="RecvHandler", target=self.udp_server)
		self.recv_thread.daemon=True
		self.recv_thread.start()
	def udp_server(self):
		while self.udpServerState:
			message, clientAddress = self.serverSocket.recvfrom(DATA_SIZE)
			message = message.decode()
			message = message.split(',')
			print(f"Ping request message received from Peer {message[1]}")
			if self.preFirstSuccessor == None :
				self.preFirstSuccessor = int(message[1]) + PORT_BIAS
			elif int(message[1]) + PORT_BIAS > self.preFirstSuccessor and int(message[1])<int(self.name):
				self.preSecondSuccessor = int(message[1]) + PORT_BIAS
			elif int(message[1]) + PORT_BIAS < self.preFirstSuccessor and self.preFirstSuccessor<self.port:
				self.preSecondSuccessor = self.preFirstSuccessor
				self.preFirstSuccessor = int(message[1]) + PORT_BIAS
			elif int(message[1])>int(self.name)and self.preFirstSuccessor>self.port and int(message[1]) + PORT_BIAS > self.preFirstSuccessor:
				self.preSecondSuccessor = int(message[1]) + PORT_BIAS
			elif int(message[1])>int(self.name)and self.preFirstSuccessor>self.port and int(message[1]) + PORT_BIAS < self.preFirstSuccessor:
				self.preSecondSuccessor = self.preFirstSuccessor
				self.preFirstSuccessor = int(message[1]) + PORT_BIAS
			elif int(message[1])>int(self.name)and self.preFirstSuccessor<self.port:
				self.preSecondSuccessor = self.preFirstSuccessor
				self.preFirstSuccessor = int(message[1]) + PORT_BIAS
			elif int(message[1])<int(self.name)and self.preFirstSuccessor>self.port:
				self.preSecondSuccessor = int(message[1]) + PORT_BIAS
			message ='response,' + self.name
			self.serverClientSocket.sendto(message.encode(), clientAddress)
	def udp_client_init(self):
		self.timer = threading.Timer(self.pingInterval,self.udp_client_init)
		self.timer.start()
		serverName = HOST
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		message = 'ping,' + self.name
		print(f"Ping requests sent to Peers {self.firstSuccessor-PORT_BIAS} and {self.secondSuccessor-PORT_BIAS}")
		serverPort = self.firstSuccessor
		self.clientSocket.sendto(message.encode(),(serverName, serverPort))
		self.clientSocket.settimeout(self.pingInterval/10)
		try :
			receivedMessage, serverAddress = self.clientSocket.recvfrom(DATA_SIZE)
			receivedMessage = receivedMessage.decode().split(',')
			print(f"Ping response received from Peer {receivedMessage[-1]}")
			self.firstSuccessorAlive = 0
		except :
			self.firstSuccessorAlive += 1
		serverPort = self.secondSuccessor
		self.clientSocket.sendto(message.encode(),(serverName, serverPort))
		self.clientSocket.settimeout(self.pingInterval/10)
		try :
			receivedMessage, serverAddress = self.clientSocket.recvfrom(DATA_SIZE)
			receivedMessage = receivedMessage.decode().split(',')
			print(f"Ping response received from Peer {receivedMessage[-1]}")
			self.secondSuccessorAlive = 0
		except :
			self.secondSuccessorAlive += 1
	def set_timer(self):
		self.timer = threading.Timer(1,self.udp_client_init)
		self.timer.start()
	def tcp_server_init(self):
		self.serverS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverS.bind((HOST, self.port))
		self.serverS.listen(5)
		while self.tcpServerState:
			conn, addr = self.serverS.accept()
			t = threading.Thread(target = self.tcp_server, args = (conn, addr)).start()
	def tcp_server(self,conn, addr):
		data = conn.recv(DATA_SIZE)
		try :
			data = data.decode().split(',')
			data[0] = data[0].lower()
		except:
			with open('./received_'+self.requestFile+'.pdf',mode='wb')as f :
				f.write(data)
				while True:
					buf = conn.recv(DATA_SIZE)
					if len(buf)<1 :
						break
					f.write(buf)
			print(f"File {self.requestFile} received")
		if data[0] == "quit":
			print(f"Peer {data[4]} will depart from the network")
			if data[1] == "first":
				print(f"My new first successor is Peer {self.firstSuccessor-PORT_BIAS}")
				print(f"My new second successor is Peer {data[2]}")
				self.secondSuccessor = int(data[2])+PORT_BIAS
			elif data[1] == "second" :
				print(f"My new first successor is Peer {data[2]}")
				print(f"My new second successor is Peer {data[3]}")
				self.firstSuccessor = self.secondSuccessor
				self.secondSuccessor = int(data[3])+PORT_BIAS
		elif data[0] == "join" :
			if (int(data[1]) + PORT_BIAS<self.firstSuccessor and int(data[1])>int(self.name)) or (self.port > self.firstSuccessor and int(data[1])+PORT_BIAS<self.firstSuccessor):
				print(f"Peer {data[1]} Join request received")
				print(f"My new first successor is Peer {data[1]}")
				print(f"My new second successor is Peer {self.firstSuccessor-PORT_BIAS}")
				message = 'accept,'+str(self.firstSuccessor-PORT_BIAS)+','+str(self.secondSuccessor-PORT_BIAS)
				tcp_send(message,int(data[1])+PORT_BIAS)
				self.secondSuccessor = self.firstSuccessor
				self.firstSuccessor = int(data[1])+PORT_BIAS
				message = 'modify,'+data[1]
				tcp_send(message,self.preSecondSuccessor)
			elif int(data[1])+PORT_BIAS<self.secondSuccessor and int(data[1])>int(self.name):
				print(f"Peer {data[1]} Join request forwarded to my successor")
				message = 'join,'+data[1]
				tcp_send(message,self.firstSuccessor)
				self.secondSuccessor = int(data[1])+PORT_BIAS
			else :
				print(f"Peer {data[1]} Join request forwarded to my successor")
				message = 'join,'+data[1]
				tcp_send(message,self.secondSuccessor)
		elif data[0] == "accept" :
			print("Join request has been accepted")
			print(f"My new first successor is Peer {data[1]}")
			print(f"My new second successor is Peer {data[2]}")
			self.firstSuccessor = int(data[1])+PORT_BIAS
			self.secondSuccessor = int(data[2])+PORT_BIAS
		elif data[0] == "modify" :
			print("Successor Change request received")
			print(f"My new first successor is Peer {self.firstSuccessor-PORT_BIAS}")
			print(f"My new second successor is Peer {data[1]}")
			self.secondSuccessor = int(data[1])+PORT_BIAS
		elif data[0] == "die" :
			message = 'die response,'+str(self.firstSuccessor-PORT_BIAS)
			if data[1] == 'first':
				tcp_send(message,self.preFirstSuccessor)
			elif data[1] == 'second' :
				tcp_send(message,self.preSecondSuccessor)
		elif data[0] == 'die response' :
			print(f"My new second successor is Peer {data[1]}")
			self.secondSuccessor = int(data[1])+PORT_BIAS
			self.secondSuccessorAlive = 0
		elif data[0] == 'store':
			if int(self.name)>= int(data[1])%MAX_NODES and self.preSecondSuccessor-PORT_BIAS<int(data[1])%MAX_NODES:
				print(f"Store {data[1]} request accepted")
			elif (int(data[1])%MAX_NODES>self.preSecondSuccessor-PORT_BIAS or int(data[1])%MAX_NODES<=int(self.name)) and self.port<self.preSecondSuccessor:
				print(f"Store {data[1]} request accepted")
			else :
				print(f"Store {data[1]} request forwarded to my successor")
				message = data[0]+','+data[1]+','+data[2]
				tcp_send(message,self.firstSuccessor)
		elif data[0] == 'request':
			if int(self.name)>= int(data[1])%MAX_NODES and self.preSecondSuccessor-PORT_BIAS<int(data[1])%MAX_NODES:
				print(f"File {data[1]} is stored here")
				print(f"Sending file {data[1]} to Peer {data[2]}")
				message = 'send file,'+data[1]+','+self.name
				tcp_send(message,int(data[2])+PORT_BIAS)
				tcp_send_file(self.name,data[1],int(data[2])+PORT_BIAS)
			elif (int(data[1])%MAX_NODES>self.preSecondSuccessor-PORT_BIAS or int(data[1])%MAX_NODES<=int(self.name)) and self.port<self.preSecondSuccessor:
				print(f"File {data[1]} is stored here")
				print(f"Sending file {data[1]} to Peer {data[2]}")
				message = 'send file,'+data[1]+','+self.name
				tcp_send(message,int(data[2])+PORT_BIAS)
				tcp_send_file(self.name,data[1],int(data[2])+PORT_BIAS)
			else :
				print(f"Request for File {data[1]} has been received, but the file is not stored here")
				message = data[0]+','+data[1]+','+data[2]
				tcp_send(message,self.firstSuccessor)
		elif data[0] == 'send file' :
			print(f"Peer {data[2]} had File {data[1]}")
			print(f"Receiving File {data[1]} from Peer {data[2]}")
		conn.close()
	def check_successor(self):
		self.detecter = threading.Timer(self.pingInterval,self.check_successor)
		self.detecter.start()
		if self.firstSuccessorAlive > MAX_LOST_PACKET:
			print(f"Peer {self.firstSuccessor-PORT_BIAS} is no longer alive")
			print(f"My new first successor is Peer {self.secondSuccessor-PORT_BIAS}")
			message = 'die,first'
			tcp_send(message,self.secondSuccessor)
			self.firstSuccessor = self.secondSuccessor
		if self.secondSuccessorAlive > MAX_LOST_PACKET :
			print(f"Peer {self.secondSuccessor-PORT_BIAS} is no longer alive")
			print(f"My new first successor is Peer {self.firstSuccessor-PORT_BIAS}")
			message = 'die,second'
			tcp_send(message,self.firstSuccessor)
	def self_loop(self):
		while True:
			message = input().lower()
			message = message.split()
			message[0] = message[0].lower()
			if message[0] == "quit" :
				quitInfo = 'quit,first,'+ str(self.firstSuccessor-PORT_BIAS)+',' + str(self.secondSuccessor-PORT_BIAS)+',' + self.name
				tcp_send(quitInfo,self.preFirstSuccessor)
				quitInfo = 'quit,second,'+ str(self.firstSuccessor-PORT_BIAS)+',' + str(self.secondSuccessor-PORT_BIAS)+',' + self.name
				tcp_send(quitInfo,self.preSecondSuccessor)
				self.timer.cancel()
				self.detecter.cancel()
				self.udpServerState = False
				self.tcpServerState = False
				sys.exit()
			elif message[0] == 'store' :
				remain = int(message[1])%MAX_NODES
				storeInfo = 'store,'+ message[1]+','+self.name
				if self.preSecondSuccessor>self.port and (remain>int(self.preSecondSuccessor-PORT_BIAS)or remain<=int(self.name)):
					print(123,self.preSecondSuccessor-PORT_BIAS)
					continue
				elif remain>self.preSecondSuccessor-PORT_BIAS and remain<=int(self.name) :
					print(456,self.preSecondSuccessor-PORT_BIAS)
					continue
				print(f"Store {message[1]} request forwarded to my successor")
				tcp_send(storeInfo,self.firstSuccessor)
			elif message[0] == 'request' :
				remain = int(message[1])%MAX_NODES
				requestInfo = 'request,'+ message[1]+','+self.name
				if self.preSecondSuccessor>self.port and (remain>int(self.preSecondSuccessor-PORT_BIAS)or remain<=int(self.name)):
					print(123,self.preSecondSuccessor-PORT_BIAS)
					continue
				elif remain>self.preSecondSuccessor-PORT_BIAS and remain<=int(self.name) :
					print(456,self.preSecondSuccessor-PORT_BIAS)
					continue
				self.requestFile = message[1]
				print(f"File request for {message[1]} has been sent to my successor")
				tcp_send(requestInfo,self.firstSuccessor)
def tcp_send(message,port):
	message = message.encode(encoding='UTF-8',errors='ignore')
	soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	soc.connect((HOST,port))
	soc.sendall(message)
	soc.close()
def tcp_send_file(name,file,port):
	soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	soc.connect((HOST,port))
	with open('./'+file+'.pdf',mode='rb') as f :
		while True:
			buf = f.read(DATA_SIZE)
			if len(buf)<1:
				soc.sendall(buf)
				break
			soc.sendall(buf)
			time.sleep(0.1)
	print("The file has been sent")
	soc.close()
if __name__ == '__main__':
	if sys.argv[1] == 'init' :
		p2p = P2P(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
		p2p.udp_server_init()
		threading.Thread(target=p2p.set_timer,args=()).start()
		threading.Thread(target=p2p.tcp_server_init,args=()).start()
		p2p.detecter.start()
	elif sys.argv[1] == 'join':
		p2p = P2P(sys.argv[2],-1,-1,sys.argv[4])
		p2p.udp_server_init()
		threading.Thread(target=p2p.tcp_server_init,args=()).start()
		message = sys.argv[1] + ',' + sys.argv[2]
		tcp_send(message,int(sys.argv[3])+PORT_BIAS)
		while p2p.secondSuccessor < PORT_BIAS :
			time.sleep(0.5)
		threading.Thread(target=p2p.set_timer,args=()).start()
		p2p.detecter.start()
	threading.Thread(target=p2p.self_loop,args=()).start()
	while True:
		time.sleep(10)