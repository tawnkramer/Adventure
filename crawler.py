import copy
from player import Player
from random import randint
import util
from skill import *
from stuff import *

'''
	The Crawler is a player bot that will crawl your level and try random stuff to try to flush out any crash bugs.
'''
class Crawler(Player):
	CRAWLING = "crawling"
	MANUAL = "manual"
	
	def __init__(self):
		#self.commands = 'search, fight, rest, look, show, inventory, wear, equip, give, drop, walk, cast, read, drink, steal'.split(', ')
		self.commands = 'search, fight, rest, look, show, inventory, cast, read, give, drink, steal'.split(', ')
		self.dir = ['N', 'S', 'E', 'W']
		self.most_common = ["fight", "search"]
		self.misc = ['l', '0', '1']
		self.state = self.CRAWLING
		util.input_handler = self
		super(Crawler, self).__init__("Crawler")
		self.skills.append(new_skill(SKILL_CAT_SHORT_EDGE))
		self.skills.append(new_skill(SKILL_CAT_ARMOR))
		self.add(WEAPON("Normal Sword"))
		self.activate(self.inventory[0])
		self.add(ARMOR("Plate Mail Armor"))
		self.activate(self.inventory[1])
		self.add(ITEM("lock pick set"))
		self.add(ITEM("rope"))
		for i in magic_items:
			self.add(copy.deepcopy(i))
		for i in all_spells:
			self.add(copy.deepcopy(i))
		self.hp = 1000
		self.cur_hp = 1000
		self.mana = 1000
		self.cur_mana = 1000
		self.gp = 1000
		self.num_commands = 10
		self.num_rounds = 0
		
	def on_combat_round_ended(self):
		super(Crawler, self).on_combat_round_ended()
		self.fully_healed()
		
	def get_input(self, prompt):
		print '"', prompt, '"', self.num_rounds
		reply = "0"
		self.num_rounds += 1
		if self.state == self.MANUAL:
			return raw_input("help! -> ")
		elif prompt.find("What would you like to do?") != -1:
			if randint(1, 4) < 3:
				reply = self.most_common[ randint(0, len(self.most_common) - 1) ]
			elif randint(1, 4) < 3:
				reply = self.dir[ randint(0, len(self.dir) - 1) ]
			else:
				reply = self.commands[ randint(0, len(self.commands) - 1)]
		elif prompt.find('a new game?') != -1:
			reply = 'y'
		elif prompt.find("y, n") != -1:
			if randint(1, 2) == 1:
				reply = 'y'
			else:
				reply = 'n'
		elif prompt.find('Enter the sel number') != -1:
			reply = str(randint(0, 1))
		elif prompt.find('name of player') != -1:
			reply = "Crawler"
		elif prompt.find('number of sel action') != -1:
			#this is combat selection
			#50% of the time, just use the sword and finish battle
			#and the rest, exercise all the spells and other combat options.
			if randint(1, 2) == 1:
				reply = str(randint(0, 100))
			else:
				reply = "1"
		elif prompt.find('item number') != -1:
			if randint(1, 2) == 1:
				reply = str(randint(0, 100))
			else:
				reply = str(randint(0, 1))
		elif prompt.find('Enter command') != -1:
			reply = 'l'
		elif prompt.find('place to walk to') != -1:
			if randint(1, 2) == 1:
				reply = str(randint(0, 100))
			else:
				reply = str(randint(0, 1))
		elif prompt.find('who to target') != -1:
			reply = str(randint(0, 10))
		elif prompt.find('number to get item') != -1:
			reply = str(randint(0, 10))
		elif prompt.find('Enter sel number') != -1:
			if randint(1, 2) == 1:
				reply = str(randint(0, 100))
			else:
				reply = str(randint(0, 1))
		else:
			self.num_commands -= 1
			reply = self.misc[ randint(0, len(self.misc) - 1)]
			if self.num_commands == 0:
				raise Exception("I'm stuck")
			elif self.num_commands < 0:
				self.state = self.MANUAL

		util.pause()
		print reply
		return reply
		