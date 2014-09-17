import pickle
import util
from player import GoodNPC
from player import Player

#this level logic can be used for mission logic that
#will get updated on each turn.
#return True when ready to remove logic
class LevelLogic(object):
	def do_update(self, room, party, level):
		return True

class Level ( object ):
	def __init__(self, name, banner=None):
		self.name = name
		self.banner = banner
		self.current_room = None
		self.party_names = [] #used for saving / loading
		self.NPCs = []
		self.levelLogic = []
		self.difficulty = 5 #from 1 to 10
		
	def add_missing_rooms(self, root_room):
		#this will compare the current latest root_room to the
		#saved list of rooms and then add any new additions.
		#existing rooms will retain their state.
		print 'Updating rooms...'
		loaded_root_room = self.current_room.find_room(root_room.name)
		if loaded_root_room is None:
			print 'Problem finding root room', root_room.name
			return
		root_room.add_missing_rooms(loaded_root_room)
		
	def add_level_logic(self, log):
		if not isinstance(log, LevelLogic):
			raise Exception("Expected to add an instance of LevelLogic, not %s to the level." % str(log))
		self.levelLogic.append(log)
		
	def update_level_logic(self, room, party):
		if util.DEBUG:
			for log in self.levelLogic:
				if log.do_update(room, party):
					self.levelLogic.remove(log)
			return
		try:
			for log in self.levelLogic:
				if log.do_update(room, party):
					self.levelLogic.remove(log)
		except:
			self.levelLogic = []
			
	def calc_party_strength(self, party):
		total_hp = 0
		total_level = 0
		total_wealth = 0
		for p in party:
			total_hp += p.hp
			total_level += p.level
			total_wealth += p.gp
			for i in p.inventory:
				if i.cost is None:
					continue
				total_wealth += i.cost.count
		num_p = len(party)
		dif = 1.0
		if num_p > 2:
			dif += (num_p - 2) * 0.05
		if total_level > 2:
			dif += (total_level - 2) * 0.05
		if total_wealth > 100:
			dif += (total_wealth / 100.0) * 0.025
		return dif
		
	def set_difficulty(self):
		dif_set = False
		while not dif_set:
			try:
				dif = util.get_input("How challenging would you like your adventure, from 1 to 10?\n 1=very easy, 5=normal, 10=very hard -> ")
				iDif = int(dif)
				if iDif >= 1 and iDif <= 10:
					self.difficulty = iDif
					dif_set = True
				else:
					print 'please enter a number between 1 and 10.'
			except:
				print 'please enter a number between 1 and 10.'
		
	#take a look at the incoming party and make an attempt to scale
	#the difficulty of the level
	def scale_difficulty(self, party):
		factor = self.difficulty / 5.
		dif = self.calc_party_strength(party) * factor
		if util.DEBUG:
			print 'calculated a party strength factor of', dif
		self.current_room.scale_difficulty(dif)
		
	def start(self, room, party):
		util.clear_screen()
		if self.banner:
			print self.banner
		else:
			print "\n--------------------------------------------"
			print "--------------------------------------------"
			print '     ', self.name
			print "--------------------------------------------"
			print "--------------------------------------------"
			print
		print
		self.current_room = room
		self.scale_difficulty(party)
		self.current_room.on_enter(party, self)
		print '\nType a command and hit the enter key. Try help for a list of commands.'
		
	def update(self, party):
		next_room = self.current_room.update(party, self)
		if next_room != self.current_room:
			self.current_room.on_exit()
			if next_room is not None:
				util.clear_screen()
				next_room.on_enter(party, self, self.current_room)
			self.current_room = next_room
		self.update_level_logic(self.current_room, party)
		return self.current_room is not None
		
	def save(self, party, room):
		if util.DEBUG:
			print "can't save debug games."
			return
		self.party_names = []
		self.NPCs = []
		for p in party:
			if isinstance(p, GoodNPC):
				self.NPCs.append(p)
			else:
				self.party_names.append(p.name)
		try:
			save_name = util.get_input('Enter a name for the save file, something you can remember later -> ')
			save_filename = self.name + '_' + save_name + '.sav'
			outfile = open(save_filename, 'wb')
			pickle.dump(self, outfile)
			outfile.close()
			print 'Saved level progress in: %s.' % save_name
		except:
			print 'Failed to save: %s. Try a different save name, perhaps with no special characters.' % save_name
		for p in party:
			if not isinstance(p, GoodNPC):
				p.save()
		
	def load(self, party):
		loaded_level = None
		
		while loaded_level is None:
			try:
				save_name = util.get_input('Enter the name of the save file -> ')
				save_filename = self.name + '_' + save_name + '.sav'
				infile = open(save_filename, 'rb')
				loaded_level = pickle.load(infile)
				infile.close()
				print 'Loaded level progress from: %s.' % save_name
			except:
				print 'Failed to load: %s. ' % save_name
				yn = util.get_input("Try again? (y, n) -> ")
				if yn == 'n':
					return None
		
		for p in party:
			party.remove(p)
		p = Player('temp')
		for name in loaded_level.party_names:
			np = p.load(name)
			party.append(np)
		try:
			for p in loaded_level.NPCs:
				party.append(p)
		except:
			if util.DEBUG:
				print 'Troubles loading NPCs.'
		loaded_level.scale_difficulty(party)
		return loaded_level		
