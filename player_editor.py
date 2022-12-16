import random
from util import *
import copy

class PlayerEditor(object):
	def __init__(self, all_skills):
		self.player = None
		self.unsaved_changes = False
		self.all_skills = all_skills
		
	def set_player(self, p):
		self.player = p
		self.unsaved_changes = False
		
	def get_command(self):
		com = get_input("Enter command: -> ")
		return com
		
	def roll_attr(self):
		if self.player.experience != 0:
			print("You can't modify your attributes once you've started adventuring!")
			return
		hi = 18
		lo = 8
		self.player.strength = random.randint(lo, hi)
		self.player.intelligence = random.randint(lo, hi)
		self.player.wisdom = random.randint(lo, hi)
		self.player.dexterity = random.randint(lo, hi)
		self.player.constition = random.randint(lo, hi)
		self.player.charisma = random.randint(lo, hi)
		self.player.hp = random.randint(4, 8) + 2
		self.player.update_attribute_mods()
		self.player.fully_healed()
		self.player.init_personality()
		self.init_gold()
		self.unsaved_changes = True
		
	def init_gold(self):
		#start with 100 gold. compensate low scores for high initial gold.
		self.player.gp = 100 - self.player.charisma
		self.player.gp -= self.player.constition
		self.player.gp -= self.player.dexterity
		self.player.gp -= self.player.wisdom
		self.player.gp -= self.player.intelligence
		self.player.gp -= self.player.strength
		if self.player.gp < 5:
			self.player.gp = 5
		
	def set_new_name(self):
		name = get_input("Enter a new name-> ")
		self.player.name = name
		self.unsaved_changes = True
		
	def set_new_sex(self):
		if self.player.sex == 'male':
			self.player.sex = 'female'
		else:
			self.player.sex = 'male'
		
	def set_new_race(self):
		print('\n Choose a race. Certain races will affect certain attributes\n')
		print(' h-human \tNo attribute changes')
		print(' o-half_orc\tstrength: +1\t\t charisma: -2')
		print(' g-halfling\tdexterity: +1\t\t strength: -1')
		print(' e-elf \t\tdexterity: +1\t\t constitution: -1')
		print(' d-dwarf\tconstitution: +1\t charisma: -1\n')
		race = get_input("Choose new race: -> ")
		self.unsaved_changes = True
		if race == 'h':
			self.player.race = 'human'
		elif race == 'o':
			self.player.race = 'half-orc'
		elif race == 'h':
			self.player.race = 'halfling'
		elif race == 'e':
			self.player.race = 'elf'
		elif race == 'd':
			self.player.race = 'dwarf'
		else:
			print("didn't recognize input")
			
	def set_new_age(self):
		self.unsaved_changes = True
		print("\nChoose an age. Certain ages will affect certain attributes.n")
		print(' 5-10:  \tstrength: -2 \twisdom: -2 \tconstitution: +2')
		print(' 11-18: \tstrength: -1 \twisdom: -1 \tconstitution: +1')
		print(' 40-60: \tstrength: -1 \twisdom: +1 \tconstitution: -1')
		print(' 60-80: \tstrength: -3 \twisdom: +3 \tconstitution: -3')
		print(' 90-99: \tstrength: -5 \twisdom: +5 \tconstitution: -5\n')
		age = get_input("Enter new age, 5-99 -> ")
		ai = int(age)
		if ai <= 99 and ai >= 5:
			self.player.age = ai
			if ai < 10:
				self.player.strength
		else:
			print("invalid age")
			
	def set_new_alignment(self):
		self.unsaved_changes = True
		print("\n Choose an option that is closest to your philosophy:\n")
		print(" n-neutral\t\t\tLive and let live. There is no good or evil except in the mind of the observer.")
		print(" lg-lawful good\t\t\tThe universe has order. And I preserve it and seek the betterment of myself and others.")
		print(" ln-lawful neutral\t\tI observe the order, but believe each man decides his own fate.")
		print(" le-lawful evil\t\t\tThere may be rules, but they exist only as a framework to advance myself.")
		print(" cg-chaotic good\t\tRules are the flimsy construct of man. What matters is only each other.")
		print(" cn-chaotic neutral\t\tRules are bars that chain me. And no one decides our destiny.")
		print(" ce-chaotic evil\t\tRules are made to be broken. And I seek to do at every opportunity.\n")
		al = get_input("Enter new alignment: -> ")
		if al == 'n':
			self.player.alignment = 'neutral'
		elif al == 'lg':
			self.player.alignment = 'lawful good'
		elif al == 'ln':
			self.player.alignment = 'lawful neutral'
		elif al == 'le':
			self.player.alignment = 'lawful evil'
		elif al == 'cg':
			self.player.alignment = 'chaotic good'
		elif al == 'cn':
			self.player.alignment = 'chaotic neutral'
		elif al == 'ce':
			self.player.alignment = 'chaotic evil'
		else:
			print("didn't recognize input")
			
	def choose_random_desc(self):
		desc = []
		desc.append("A lone, and lonely wolf. Cast out from his tribe, adrift in the wilderness.")
		desc.append("A fighter, always struggling to prove his worth. Always looking for conflict.")
		desc.append("A wanderer, always curious about where this stream will lead, and what lies over the hill.")
		desc.append("A searcher, looking for the precious bit of knowledge to make everything clear.")
		desc.append("A comdian, always looking for a laugh. Never sure why people take things so seriously.")
		desc.append("A mystic, intrigued with the mysterious ways the universe presents herself.")
		iChoice = random.randint(0, len(desc) - 1)
		return desc[iChoice]	
	
	def set_new_description(self):
		self.unsaved_changes = True
		desc = get_input("Type a new description or hit r to make a random one: -> ")
		if desc == 'r':
			desc = self.choose_random_desc()
		self.player.description = desc
		
	def choose_new_skills(self):
		self.unsaved_changes = True
		print('\n Skills:\n')
		print('sel\tcost\tname\t\t\t\tdescription')
		num = len(self.all_skills)
		for i in range(0, num):
			s = self.all_skills[i]
			print(i+1,'\t', s.cost, '\t', s.name, s.description)
		done = False
		while not done:
			print('\nYou have', self.player.sp, 'skill points to spend.')
			ch = get_input('Type the sel number of the skill you wish to aquire or improve (e-exit)-> ')
			if ch == 'e':
				done = True
				break
			try:
				ch_i = int(ch)
			except:
				print('invalid input')
				continue
			if ch_i <= 0 or ch_i > num:
				print('input out of range')
				continue
			sel_s = self.all_skills[ch_i - 1]
			if sel_s.cost > self.player.sp:
				print('The skill', sel_s.name, 'costs', sel_s.cost, 'but you have only', self.player.sp, 'skill points.')
			else:
				yn = get_input('Are you sure %s wants %s training? (y, n) -> ' % (self.player.name, sel_s.name))
				if yn == 'y':
					if sel_s.uses_mana():
						self.player.update_attribute_mods()
						mana_pt = random.randint(4, 8) + self.player.mana_mod
						print(self.player.name, "gains %d mana with %s training." % ( mana_pt, self.player.get_pronoun_lower()))
						self.player.mana += mana_pt
					self.player.sp -= sel_s.cost
					sk = self.player.get_skill(sel_s.cat)
					if sk is not None:
						sk.level += 1
						print(self.player.name, 'now has', sel_s.name, 'training level %d.' % sk.level)
					else:
						self.player.skills.append(copy.deepcopy(sel_s))
						print(self.player.name, 'now has', sel_s.name, 'training.')
			
	def load_player(self):
		name = get_input("Enter the name of the player to load -> ")
		loaded_player = self.player.load(name)
		if loaded_player is not None:
			self.set_player(loaded_player)
		
	def print_help(self, isNewChar):
		if isNewChar:
			print("\n r-roll for new attributes\n n-set new name\n l-set new alignment\n d-set new description\n a-set new age\n c-set new race\n k-choose new skills\n p-new personality\n x-change sex\n s-save\n o-load\n e-exit\n")
		else:
			print("\n n-set new name\n l-set new alignment\n d-set new description\n a-set new age\n c-set new race\n k-choose new skills\n p-new personality\n x-change sex\n s-save\n o-load\n e-exit\n")
		
	def do_edit(self, p, isNewChar=True):
		self.set_player(p)
		done = False
		doWelcome=isNewChar
		while not done:
			self.player.show()
			self.print_help(isNewChar)
			if doWelcome:
				doWelcome = False
				print(' Welcome to your player creator. This is where we get to decide all the details about yourself.\n Try hitting r a few times until you see some attribute numbers you like. The attributes go from 3 to 18.\n Then choose your skills. If you like, you can change the other things too. But attributes and skills are most important.\n Have fun!')
			com = self.get_command()
			if com == 'e':
				if self.unsaved_changes:
					cont = get_input("You have unsaved changes. Would you like to exit? y, n -> ")
					if cont == 'y':
						done = True
				else:
					done = True
			elif com == 'r' and isNewChar:
				self.roll_attr()
			elif com == 'n':
				self.set_new_name()
			elif com == 'p':
				self.player.init_personality()
			elif com == 'l':
				self.set_new_alignment()
			elif com == 'd':
				self.set_new_description()
			elif com == 'a':
				self.set_new_age()
			elif com == 'c':
				self.set_new_race()
			elif com == 'x':
				self.set_new_sex()
			elif com == 'k':
				self.choose_new_skills()
			elif com == 's':
				if self.player.save():
					self.unsaved_changes = False
			elif com == 'o':
				self.load_player()
			else:
				print("Sorry, didn't recognize command:", com)
				

 
