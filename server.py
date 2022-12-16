import os, sys, signal, time, pickle, zlib
from subprocess import Popen, PIPE, STDOUT
import socket, threading
from select import select

VERBOSE = False

class adventure_app(object):
	def __init__(self, logfilename, levelname):
		self.levelname = levelname
		self.logfilename = logfilename
		self.logfile = None
		self.process = None
		
	def run(self):
		#the -u lets us process the output as it happens, without buffering
		#the online arg lets our adventure know to operate in a slightly different mode.
		command = ['python', '-u', self.levelname, 'online']
		
		if VERBOSE:
			print('starting subprocess with', command)
		
		#start the process and let it run.
		self.process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		self.start_log()
		
	def start_log(self):
		if self.logfile is not None:
			self.logfile.close()
		self.logfile = open(self.logfilename, "wt")
		
	def poll_io(self, output_arr):
		if self.process is None:
			return False
		if self.process.returncode is not None:
			print('terminated with', self.process.returncode)
			return False
		line = self.process.stdout.readline()
		if line == '' and self.process.poll() != None:
			return False
		if len(line) > 0:
			output_arr.append(line.decode())
			if self.logfile is not None:
				self.logfile.write(line.decode())
		return True
		
	def push_io(self, line):
		if self.process is not None:
			self.process.stdin.write(line.encode())
			self.process.stdin.write('\n'.encode())
			self.process.stdin.flush()
	
	def stop(self):
		if VERBOSE:
			print('stopping app subprocess')
		try:
			if self.process is not None:
				self.process.terminate()
				self.process = None
			if self.logfile is not None:
				self.logfile.close()
				self.logfile = None
		except:
			self.process = None
			self.logfile = None

class app_runner(object):
	def __init__(self):
		self.clients = []
		self.app = None
		self.local_echo = False
		self.level_name = 'TheRaggedKeep.py'
		
	def send_clients(self, data):
		for c in self.clients:
			c.send(data)
			
	def on_input(self, line):
		if self.app is not None:
			self.app.push_io(line)
			
	def stop(self):
		if self.app is not None:
			self.app.stop()
			
	def set_level_name(self, filename):
		self.level_name = filename
			
	def run(self):
		self.app = adventure_app('log.txt', self.level_name)
		self.app.run()
		output = []
		try:
			while self.app.poll_io(output):
				if self.local_echo or VERBOSE:
					for line in output:
						sys.stdout.write(line)
						sys.stdout.flush()
				flush = False
				for line in output:
					if line.find('->') != -1:
						flush = True
				
				if len(output) > 0 and flush:
					self.send_clients(''.join(output))
					output = []
		except Exception as err:
			print(Exception, err)
			self.app = None
			
	def threaded_run(self):
		t = threading.Thread(target=self.run)
		t.daemon = True
		t.start()
						
class GameClient(object):
	def __init__(self, sock, addr):
		self.sock = sock
		self.addr = addr
		self.name = 'Someone'
		self.to_send = None
		self.lock = threading.Lock()
		
	def send(self, data):
		with self.lock:
			if self.to_send is None:
				self.to_send = []
			self.to_send.append(data)

	def poll(self, receiver):
		if True: #try:
			readable, writable, exceptional = select([self.sock], [], [], 0.0001)
			if readable:
				data = self.sock.recv(4096).decode('utf-8')
				if data:
					receiver.on_recv_client_data(data, self)
			with self.lock:
				if self.to_send is not None:
					for data in self.to_send:
						if VERBOSE:
							print('sending', data)
						self.sock.sendall(data.encode())
					self.to_send = None
			if exceptional:
				print('maybe this connection closed?')
		#except:
		#	pass
			
class GameLevel(object):
	def __init__(self, filename, description):
		self.filename = filename
		self.description = description
		
	def show(self, output):
		output.append( self.description )
	
class GameServer(object):
	def __init__(self):
		self.clients = []
		self.the_app = app_runner()
		self.output = []
		self.game_levels = []
		self.waiting_on_level_choice = False
		self.quit_app = False
		
	def add_game_level(self, level):
		self.game_levels.append(level)
		
	def get_level_choices(self):
		i = 1
		output = []
		output.append('Available levels:\n')
		for l in self.game_levels:
			output.append( "%d)\n" % i )
			l.show(output)
			output.append("\n\n")
			i += 1
		output.append("Enter the number of level to play ->\n\n")
		self.waiting_on_level_choice = True
		self.broadcast(''.join(output))
		
	def make_level_choice(self, input):
		try:
			self.waiting_on_level_choice = False
			iChoice = int(input) - 1
			level = self.game_levels[iChoice]
			self.the_app.set_level_name(level.filename)
			self.the_app.threaded_run()
		except:
			self.broadcast('Failed to start level\n')
			
	def broadcast(self, message):
		for c in self.clients:
			c.send(message)
		
	def add_client(self, client):
		self.clients.append(client)
		
	def poll(self):
		for c in self.clients:
			if True: #try:
				c.poll(self)
			else: #except Exception as err:
				print(Exception, err)
				print(c.name, 'dropped connection')
				self.the_app.clients.remove(c)
				self.clients.remove(c)
				for oc in self.clients:
					oc.send('%s dropped connection.\n' % c.name)
				
	def on_recv_client_data(self, data, client):
		if data.find('<player>') == -1:
			print('got', data)
		if data.find('<login>') != -1:
			args = data.split('|')
			if len(args) == 2:
				name = args[1]
				client.name = name
				self.the_app.clients.append(client)
				print('added client', name)
				welcomeStr = 'Welcome %s!\n' % name
				if len(self.clients) == 1:
					for arg in sys.argv:
						if arg == '--local':
							self.get_level_choices()
							#self.the_app.threaded_run()
							return
					welcomeStr += 'You are the first one here.\n'
					welcomeStr += 'Type /r when you are ready to start the game.\n'
					welcomeStr += 'Type / to chat.\n'
					#welcomeStr += 'Type /u to upload a player file.\n'
				else:
					welcomeStr += 'Type / to chat.\n'
					#welcomeStr += 'Type /u to upload a player file.\n'
					for c in self.clients:
						if c == client:
							continue
						welcomeStr += '%s is here.\n' % c.name						
						c.send('%s is here.\n' % name)
				client.send(welcomeStr)		
		elif data.find('<run>') != -1:			
			self.get_level_choices()
			#self.the_app.threaded_run()
		elif data.find('<quit>') != -1:
			name = client.name
			print(name, 'is quiting.')
			self.the_app.clients.remove(client)
			self.clients.remove(client)
			self.broadcast('%s left.\n' % name)
			if len(self.clients) == 0:
				self.the_app.on_input('q')
				self.the_app.stop()
				for arg in sys.argv:
					if arg == '--local':
						self.quit_app = True
					
		elif data.find('<input>') != -1:
			args = data.split('|')
			if len(args) == 2:
				line = args[1]
				if self.waiting_on_level_choice:
					self.make_level_choice(line)
				else:
					for c in self.clients:
						c.send('%s\n' % line)
					self.the_app.on_input(line)
		elif data.find('<chat>') != -1:
			args = data.split('|')
			if len(args) == 2:
				line = args[1]
				for c in self.clients:
					if c == client and False: #do echo back to client?
						continue
					c.send('%s\n' % line)
		elif data.find('<player>') != -1:
			data = data[len('<player>'):]
			loaded_player = pickle.loads(zlib.decompress(data))
			loaded_player.save()
				
class ConnectionServer(object):

	def __init__(self, host, port, game_server):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setblocking(False)
		self.sock.bind((host, port))
		self.sock.listen(5)
		self.game_server = game_server
		print('listening on', port)

	def poll(self):
		try:
			pair = self.sock.accept()
			if pair is None:
				pass
			else:
				sock, addr = pair
				print('Incoming connection from %s' % repr(addr))
				client = GameClient(sock, addr)
				self.game_server.add_client(client)
		except:
			pass

trk = GameLevel('TheRaggedKeep.py',
'''
            The Ragged Keep
	
   Part I of III in the Adventures at Aclovar
         For 2-6 players level 1-3
Take on the challenge of the dungeons of The Ragged Keep
    and discover the dark secrets of the Baron.
	           
           Written by Tawn Kramer
			   
Recommended Teen. Mild Fantasy Violence, Intense Situations''')
		
coc = GameLevel('CavesOfChaos.py',
'''
            Caves of Chaos
	
   Part II of III in the Adventures at Aclovar
         For 2-6 players level 1-3
Help save the town of Aclovar by taking on the quest in the
         mysterious Caves of Chaos.
	           
          Written by Tawn Kramer
Based on Keep on the Boarderlands by Gary Gygax
			   
Recommended Teen. Mild Fantasy Violence, Intense Situations''')
				
def serve():
	HOST, PORT = "0.0.0.0", 9999
	
	for arg in sys.argv:
		if arg.find('-v') != -1:
			global VERBOSE
			VERBOSE = True

	#poll the clients and handle send and recv with them.
	gs = GameServer()
	
	#add levels
	gs.add_game_level(trk)
	gs.add_game_level(coc)
	
	# Create the server, binding to localhost on port 9999
	cs = ConnectionServer(HOST, PORT, gs)

	# poll the services; this will keep running until you
	# interrupt the program with Ctrl-C
	while not gs.quit_app:
		gs.poll()
		cs.poll()
	
serve()

	