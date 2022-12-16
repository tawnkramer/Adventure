import os, sys, pickle, zlib
import socketserver, socket, threading
from select import select
import util

class GameClient(object):
	def __init__(self, sock):
		self.sock = sock
		self.sock.setblocking(False)
		self.to_send = None
		
	def send(self, data):
		#print 'queueing', data
		self.to_send = data

	def poll(self):
		if True: #try:
			readable, writable, exceptional = select([self.sock], [], [], 0.0001)
			if readable:
				data = self.sock.recv(4096)
				if data:
					if data.find('<cls>') != -1:
						util.clear_screen()
						data = data.replace('<cls>', '')
					sys.stdout.write(data)
					sys.stdout.flush()
			if True: #writable:
				if self.to_send is not None:
					#print 'sending', self.to_send
					self.sock.sendall(self.to_send)
					self.to_send = None
			if exceptional:
				print('maybe this connection closed?')
		else:#except:
			pass
			
#This works, but is not cross platform. Windows complains that select
#can't be used on something, sys.stdin, that is not a socket
def poll_stdin(typed):
	i,o,e = select([sys.stdin],[],[],0.0001)
	for s in i:
		if s == sys.stdin:
			data = sys.stdin.readline()
			typed.append(data)
			return True
	return False
	
class InputPoll(object):
	def __init__(self):
		self.input = None
		self.keep_polling = True
		
	def poll_raw_input(self):
		while self.keep_polling:
			self.input = input('')

poller = InputPoll()

def start_polling_input():
	t = threading.Thread(target=poller.poll_raw_input)
	t.daemon = True
	t.start()
	
def stop_polling_input():
	poller.keep_polling = False
	
def get_input(input_arr):
	if poller.input is not None:
		input_arr.append(poller.input)
		poller.input = None		
	return len(input_arr) > 0
			
def main():
	SERVER_PORT = 9999
	server_ip = 'localhost'
	name = 'Someone'
	
	if len(sys.argv) < 3:
		print('usage - python client.py server=serverip name=clientname')
		return
	
	for arg in sys.argv:
		if arg.find('server=') != -1:
			args = arg.split('=')
			if len(args) == 2:
				server_ip = args[1]
				#print '>setting server ip to', server_ip
		if arg.find('name=') != -1:
			args = arg.split('=')
			if len(args) == 2:
				name = args[1]
				#print '>setting client name to', name

	# connect to server
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((server_ip, SERVER_PORT))
	except:
		print('Failed to connect to server.')
		return
	
	#start thread polling for input
	start_polling_input()
	
	#login to server
	gc = GameClient(sock)
	gc.send('<login>|%s' % name)
	
	typed = []
	
	while True:
		gc.poll()
		try:
			ret = get_input(typed)
		except:
			ret = False
		if ret:
			data = ''.join(typed)
			typed = []	
			if data == 'q':
				gc.send('<quit>|%s' % name)
				stop_polling_input()
				return
			elif len(data) == 2 and data[0] == ('/') and data[1] == ('u'):
				print('Enter player to send-> ')
				typed = []
				while not get_input(typed):
					pass
				player_name = ''.join(typed)
				filename = player_name + '.plr'
				try:
					infile = open(filename, "rb")
					loaded_player = pickle.load(infile)
					infile.close()
					pickeled_player = zlib.compress(pickle.dumps(loaded_player))					
					gc.send('<player>' + pickeled_player)
					print('sent player file in', len(pickeled_player), 'bytes.')
				except:
					print('sorry, it failed.')
			elif data == '/r':
				gc.send('<run>')
			elif len(data) > 1 and data[0] == ('/'):
				gc.send('<chat>|%s says "%s"' % (name, data[1:]))
			else:
				gc.send('<input>|%s' % data)

main()



		
	
