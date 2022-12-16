import os, sys, pickle, zlib
import socketserver, socket, threading, time
from select import select
from subprocess import Popen, PIPE, STDOUT
import wx

username = 'user'
SERVER_PORT = 9999
server_ip = '192.168.2.25'

class GameClient(object):
	def __init__(self, sock):
		self.sock = sock
		self.sock.setblocking(False)
		self.to_send = None
		
	def send(self, data):
		#print 'queueing', data
		self.to_send = data

	def poll(self, output):
		if True: #try:
			readable, writable, exceptional = select([self.sock], [], [], 0.0001)
			if readable:
				data = self.sock.recv(4096)
				if data:
					output.append(data)
			if True: #writable:
				if self.to_send is not None:
					#print 'sending', self.to_send
					self.sock.sendall(self.to_send)
					self.to_send = None
			if exceptional:
				print('maybe this connection closed?')
		else:#except:
			pass
						
class server_app(object):
	def __init__(self):
		self.process = None
		
	def run(self):
		#start the server as a local process we will connect to.
		command = ['python', 'server.py', '--local']
		
		#start the process and let it run.
		self.process = Popen(command)
		
	def stop(self):
		if self.process is not None:
			try:
				self.process.terminate()
			except:
				pass
			while self.process.poll() is None:
				pass
			if self.process.returncode is not None:
				print('process is closed')
				self.process = None
		
	def poll(self):
		if self.process is None:
			return
		self.process.poll()
		if self.process.returncode is not None:
			print('process is closed')
			self.process = None
			
class NewServerDefDialog(wx.Dialog):
	def __init__(self, *args, **kw):
		super(NewServerDefDialog, self).__init__(*args, **kw)
		self.SetSize((400, 300))
		self.SetTitle("Add New Server Connection")
		self.username = None
		self.InitUI()
		self.Center()
		
	def InitUI(self):
		panel = wx.Panel(self)
		panel.SetSize((400, 300))
		userLabel = wx.StaticText(panel, pos=(10, 10), label="Name - visible to others during chat")
		self.usernameCtrl = wx.TextCtrl(panel, -1, '', pos=(10, 30), size=(250, 20))
		
		serverIpLabel = wx.StaticText(panel, pos=(10, 60), label="Server IP address")
		self.ipCtrl = wx.TextCtrl(panel, -1, 'localhost', pos=(10, 80), size=(250, 20))
		
		portLabel = wx.StaticText(panel, pos=(10, 110), label="Server Port")
		self.portCtrl = wx.TextCtrl(panel, -1, '9999', pos=(10, 130), size=(250, 20))
		
		configLabel = wx.StaticText(panel, pos=(10, 160), label="Config name")
		self.configNameCtrl = wx.TextCtrl(panel, -1, 'A Local Server', pos=(10, 180), size=(250, 20))
		
		okButton = wx.Button(panel, label='Ok', pos=(100, 230))
		cancelButton = wx.Button(panel, label='Cancel', pos=(200, 230))
		okButton.Bind(wx.EVT_BUTTON, self.OnSave)
		cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
		
	def OnSave(self, e):
		self.username = self.usernameCtrl.GetValue()
		self.ip = self.ipCtrl.GetValue()
		self.port = int(self.portCtrl.GetValue())
		self.configname = self.configNameCtrl.GetValue()		
		self.OnClose(e)
		
	def OnClose(self, e):
		self.Close()
		#self.Destroy()
		
class NewDefaultUsernameDialog(wx.Dialog):
	def __init__(self, *args, **kw):
		super(NewServerDefDialog, self).__init__(*args, **kw)
		self.SetSize((400, 300))
		self.SetTitle("Set Default Username")
		self.Center()
		self.username = None
		self.InitUI()		
		
	def InitUI(self):
		panel = wx.Panel(self)
		panel.SetSize((300, 100))
		userLabel = wx.StaticText(panel, pos=(10, 10), label="Name - visible to others during chat")
		self.usernameCtrl = wx.TextCtrl(panel, -1, '', pos=(10, 30), size=(250, 20))
		
		okButton = wx.Button(panel, label='Ok', pos=(100, 70))
		cancelButton = wx.Button(panel, label='Cancel', pos=(200, 70))
		okButton.Bind(wx.EVT_BUTTON, self.OnSave)
		cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
		
	def OnSave(self, e):
		self.username = self.usernameCtrl.GetValue()
		self.OnClose(e)
		
	def OnClose(self, e):
		self.Destroy()

		
class ServerConfig(object):
	def __init__(self, user, ip, port, name):
		self.user = user
		self.ip = ip
		self.port = port
		self.name = name
		
class ServerConfigs(object):
	def __init__(self):
		self.configs = []
		self.default_username = None
		
	def save(self, filename):
		try:
			outfile = open(filename, 'wb')
			pickle.dump(self, outfile)
			outfile.close()
		except:
			pass
		
	def load(self, filename):
		try:
			infile = open(filename, 'rb')
			new_conf = pickle.load(infile)
			infile.close()
			return new_conf
		except:
			pass
		return self

class MyFrame(wx.Frame):
	def __init__(self, *args, **kwargs):
		super(MyFrame, self).__init__(*args, **kwargs)
		self.SetSize((1200, 1000))
		self.SetTitle("Adventure Win Client")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.config_filename = "server_configs.cfg"		
		self.local_server = None
		
		menuBar = wx.MenuBar()
		file_menu = wx.Menu()
		m_exit = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
		self.Bind(wx.EVT_MENU, self.onClose, m_exit)
		menuBar.Append(file_menu, '&App')
		
		self.run_menu = wx.Menu()
		m_run_local = self.run_menu.Append(1, "&Run local\tAlt-R", "Run a local game.")
		m_add_server_connection = self.run_menu.Append(3, "&Add Server\tAlt-A", "Add a new server definition.")
		self.Bind(wx.EVT_MENU, self.onRunLocal, m_run_local)
		self.Bind(wx.EVT_MENU, self.onAddServerConnection, m_add_server_connection)
		
		menuBar.Append(self.run_menu, 'Run')
		
		font_menu = wx.Menu()
		m_choose_font = font_menu.Append(10, "Choose F&ont\tAlt-O", "Select a font")
		self.Bind(wx.EVT_MENU, self.onChooseFont, m_choose_font)
		m_set_default_font = font_menu.Append(11, "Revert to &Default Font\tAlt-D", "Change back to default monospace font")
		self.Bind(wx.EVT_MENU, self.onRevertToDefaultFont, m_set_default_font)
		menuBar.Append(font_menu, 'Font')
		
		self.SetMenuBar(menuBar)

		self.gc = None
		self.typed = None
		panel = wx.Panel(self)
		self.outputCtrl = wx.TextCtrl(panel, pos=(10, 10), size=(1180, 600), style=wx.TE_MULTILINE)
		self.inputCtrl = wx.TextCtrl(panel, -1, 'Type input here', pos=(10, 620), size=(1180, 20), style=wx.TE_PROCESS_ENTER)
		
		
		self.font1 = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, False)
		self.outputCtrl.SetFont(self.font1)

		self.inputCtrl.Bind(wx.EVT_TEXT_ENTER, self.onInput)
		self.inputCtrl.Bind(wx.EVT_LEFT_DOWN, self.onClickInput)
		panel.Bind(wx.EVT_SIZE, self.onSize)
		
		self.Center()
		
		sc = ServerConfigs()
		self.server_configs = sc.load(self.config_filename)
		self.bind_server_configs()
		
		self.init_app()
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
		self.timer.Start(10)
		
		panel.SetFocus()		
		self.Show(True)
		
	def onClose(self, event):
		self.quit_server_connection()
		self.close_local_run()
		self.Destroy()
		
	def onChooseFont(self, event):
		fd = wx.FontData()
		fd.SetInitialFont(self.font1)
		dialog = wx.FontDialog(None, fd)
		if dialog.ShowModal() == wx.ID_OK:
			data = dialog.GetFontData()
			self.font1 = data.GetChosenFont()
			self.outputCtrl.SetFont(self.font1)
		dialog.Destroy()
		
	def get_server_config(self, iConfig):
		return self.server_configs.configs[iConfig]
		
	def onConnectTo(self, iConfig):
		self.close_local_run()
		try:
			sc = self.get_server_config(iConfig)
			self.connect_to_server(sc.ip, sc.port)
		except:
			pass
		
	def onConnect0(self, event):
		print("hey, I'm dynamically bound 0")
		self.onConnectTo(0)
		
	def onConnect1(self, event):
		print("hey, I'm dynamically bound 1")
		self.onConnectTo(1)
		
	def onConnect2(self, event):
		print("hey, I'm dynamically bound 2")
		self.onConnectTo(2)
		
	def onConnect3(self, event):
		print("hey, I'm dynamically bound 3")
		self.onConnectTo(3)
		
	def onConnect4(self, event):
		print("hey, I'm dynamically bound 4")
		self.onConnectTo(4)
		
	def onAddServerConnection(self, event):
		dlg = NewServerDefDialog(self)
		dlg.ShowModal()
		if dlg.username is not None:
			iBind = len(self.server_configs.configs)
			dyn_bind = '''self.Bind(wx.EVT_MENU, self.onConnect%d, new_connection)''' % (iBind)
			nc = ServerConfig(dlg.username, dlg.ip, dlg.port, dlg.configname) 
			self.server_configs.configs.append(nc)
			self.server_configs.save(self.config_filename)
			new_connection = self.run_menu.Append(4 + iBind, "Connect: %s" % dlg.configname, "Connect to remote server.")
			exec(dyn_bind)
		
		dlg.Destroy()
		
	def bind_server_configs(self):
		iConfig = 0
		for conf in self.server_configs.configs:
			dyn_bind = '''self.Bind(wx.EVT_MENU, self.onConnect%d, new_connection)''' % (iConfig)
			new_connection = self.run_menu.Append(iConfig + 4, "Connect: %s" % conf.name, "Connect to remote server.")
			exec(dyn_bind)
			iConfig += 1
		
	def onRevertToDefaultFont(self, event):
		self.font1 = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, False)
		self.outputCtrl.SetFont(self.font1)
		
	def init_app(self):
		self.outputCtrl.AppendText("Welcome to the windows adventure client.\n")
		self.outputCtrl.AppendText("You can run a solo adventure locally by using the menu. Select Run | Run local.\n")
		self.outputCtrl.AppendText("You can play with others by connecting to their servers. Select Run | Add Server. Fill in the details. Then it will make a new menu item under Run | Connect: Server Description . Select that to make the connection.\n")
	
	def onSize(self, event):
		sz = self.GetClientSize()
		margin_r = 20
		margin_b = 50
		self.outputCtrl.SetSize((sz[0] - margin_r, sz[1] - margin_b))
		self.inputCtrl.SetPosition((10, sz[1] - margin_b + 20))
		self.inputCtrl.SetSize((sz[0] - margin_r, 20))
		
	def clearOutput(self):
		self.outputCtrl.Clear()
		self.outputCtrl.SetFont(self.font1)
		
	def onRunLocal(self, event):
		self.close_local_run()
		self.local_server = server_app()
		self.local_server.run()
		time.sleep(3)
		self.connect_to_server("127.0.0.1", SERVER_PORT)
		
	def close_local_run(self):
		if self.local_server is None:
			return
		self.local_server.stop()
		self.local_server = None
		
	def onBrowse(self, event):
		dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.self", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.executableCtrl.SetValue(path)
			global exec_path
			exec_path = path
			filename = path.split('\\')[-1]
			filepath = path[:-len(filename) - 1]
			self.app.executable = filename
			self.app.path = filepath
			write_prefs()
		dlg.Destroy()
			
	def connect_to_server(self, ip, port):
		self.quit_server_connection()
		try:
			wx.BeginBusyCursor()
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((ip, port))
			wx.EndBusyCursor()
		except:
			self.outputCtrl.AppendText('Failed to connect to server: %s:%d\n' %(ip, port))
			wx.EndBusyCursor()
			return
				
		#login to server
		self.clearOutput()
		self.gc = GameClient(sock)
		self.gc.send('<login>|%s' % username)
		
	def onInput(self, event):
		self.typed = self.inputCtrl.GetValue()
		self.inputCtrl.Clear()
		
	def onClickInput(self, event):
		val = self.inputCtrl.GetValue()
		if val == 'Type input here':
			self.inputCtrl.Clear()
		self.inputCtrl.SetFocus()
		
	def onUserName(self, event):
		global username
		username = self.usernameCtrl.GetValue()
		self.outputCtrl.AppendText("Welcome %s!\n" % username)
		write_prefs()
		
	def quit_server_connection(self):
		if self.gc is None:
			return
		output = []
		self.gc.send('<quit>|%s' % username)
		self.gc.poll(output) #to do one last send
		self.clearOutput()
		self.gc = None
  
	def update(self, event):
		if self.local_server is not None:
			self.local_server.poll()
			
		if self.gc is None:
			return	
		output = []
		try:
			self.gc.poll(output)
		except:
			self.gc = None
			self.outputCtrl.AppendText("disconnect from server.")
			return
		for line in output:
			if line.find('<cls>') != -1:
				self.clearOutput()
				line = line.replace('<cls>', '')
			self.outputCtrl.AppendText(line)
		
		if self.typed is not None:
			data = self.typed
			self.typed = None
			if data == 'q':
				self.quit_server_connection()
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
				self.gc.send('<run>')
			elif len(data) > 1 and data[0] == ('/'):
				self.gc.send('<chat>|%s says "%s"' % (username, data[1:]))
			else:
				self.gc.send('<input>|%s' % data)
	
	def Close(self):
		self.timer.Stop()

if '__main__' == __name__:
    app = wx.PySimpleApp()
    frame = MyFrame(None)
    app.MainLoop()
		
	
