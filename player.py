'''
Player class

'''
import pickle
from prettytable import PrettyTable, HEADER

import player_editor
import util
from skill import *
from commentary import get_random_trait
from commentary import TRAIT
			
##################################################
## Player Class
			
class Player(object):
	def __init__(self, name):
		self.name = name
		self.race = 'human'
		self.hp = 10
		self.cur_hp = self.hp #hp keeps track of max, cur_hp what we have currently
		self.armor_class = 9
		self.experience = 0
		self.level = 1
		self.strength = 10
		self.intelligence = 10
		self.wisdom = 10
		self.dexterity = 10
		self.constitution = 10
		self.charisma = 10
		self.alignment = "neutral"
		self.inventory = [ ]
		self.active_weapon = None
		self.active_armor = None
		self.active_shield = None
		self.active_items = []
		self.description = 'a normal dude'
		self.history = []
		self.sex = 'male'
		self.age = 20
		self.gp = 0
		self.sp = 0
		self.cp = 0
		#attribute modifiers
		self.str_mod = 0
		self.int_mod = 0
		self.wis_mod = 0
		self.dex_mod = 0
		self.con_mod = 0
		self.chr_mod = 0
		self.ac_mod = 0
		self.hp_mod = 0
		self.version = 2
		#as we add more fields, use version to correct saved players
		self.skills = []
		self.sp = 4 #skill points
		self.disabled = 0
		self.mana = 0
		self.cur_mana = 0
		self.hidden = False
		self.trapped = None
		self.personality = []
		self.traits = [] #numbers which correlate the personality above
		
	def on_action(self, action_name, item, other):
		if(action_name == 'give'):
			print self.name, 'says thanks!'
			return True
		print self.name, 'shrugs unsure of what', action_name, 'means.'
		return False

		
	def update_attribute_mods(self):
		self.str_mod = 0
		self.int_mod = 0
		self.wis_mod = 0
		self.dex_mod = 0
		self.con_mod = 0
		self.chr_mod = 0
		self.ac_mod = 0
		self.hp_mod = 0
		self.mana_mod = 0
		
		#age based mods. Not factoring in race right now.
		if(self.age < 11):
			self.str_mod = -2
			self.wis_mod = -2
			self.con_mod = 2
		elif(self.age < 19):
			self.str_mod = -1
			self.wis_mod = -1
			self.con_mod = 1
		elif(self.age < 40):
			pass
		elif(self.age < 61):
			self.str_mod = -1
			self.wis_mod = 1
			self.con_mod = -1
		elif(self.age < 81):
			self.str_mod = -3
			self.wis_mod = 3
			self.con_mod = -3
		elif(self.age >= 90):
			self.str_mod = -5
			self.wis_mod = 5
			self.con_mod = -5
			
		#race based mods
		if self.race == 'half-orc':
			self.str_mod += 1
			self.chr_mod += -2
		elif self.race == 'halfling':
			self.dex_mod += 1
			self.str_mod += -1
		elif self.race == 'elf':
			self.dex_mod += 1
			self.con_mod += -1
		elif self.race == 'dwarf':
			self.chr_mod += -1
			self.con_mod += 1
			
		#hp mods
		adj_con = self.constitution + self.con_mod
		if adj_con <= 8:
			self.hp_mod = -1
		elif adj_con <= 12:
			self.hp_mod = 0
		elif adj_con <= 15:
			self.hp_mod = 1
		elif adj_con <= 17:
			self.hp_mod = 2
		elif adj_con <= 18:
			self.hp_mod = 3
		elif adj_con <= 19:
			self.hp_mod = 4
		elif adj_con <= 20:
			self.hp_mod = 5
			
		#ac mods
		adj_dex = self.dexterity + self.dex_mod
		if adj_dex <= 8:
			self.ac_mod = 1
		elif adj_dex <= 12:
			self.ac_mod = 0
		elif adj_dex <= 15:
			self.ac_mod = -1
		elif adj_dex <= 17:
			self.ac_mod = -2
		elif adj_dex <= 18:
			self.ac_mod = -3
		elif adj_dex <= 19:
			self.ac_mod = -4
		elif adj_dex <= 20:
			self.ac_mod = -5
						
		self.update_armor_class()
			
		try:
			if self.magic_shield > 0:
				self.ac_mod -= 9
		except:
			pass
			
		#mana_mods
		adj_int = self.intelligence + self.int_mod
		if adj_int <= 8:
			self.mana_mod = -1
		elif adj_int <= 12:
			self.mana_mod = 0
		elif adj_int <= 15:
			self.mana_mod = 1
		elif adj_int <= 17:
			self.mana_mod = 2
		elif adj_int <= 18:
			self.mana_mod = 3
		elif adj_int <= 19:
			self.mana_mod = 4
		elif adj_int <= 20:
			self.mana_mod = 5
		
		adj_wis = self.wisdom + self.wis_mod
		if adj_wis <= 8:
			self.mana_mod += -1
		elif adj_wis <= 12:
			self.mana_mod += 0
		elif adj_wis <= 15:
			self.mana_mod += 1
		elif adj_wis <= 17:
			self.mana_mod += 2
		elif adj_wis <= 18:
			self.mana_mod += 3
		elif adj_wis <= 19:
			self.mana_mod += 4
		elif adj_wis <= 20:
			self.mana_mod += 5
		
	def get_strength(self):
		bs = 0
		if self.is_blessed():
			bs = 3
		return self.strength + self.str_mod + bs
		
	def get_damage_mod(self):
		if util.DEBUG:
			return 100
		s = self.get_strength()
		if s <= 8:
			return -1
		if s <= 12:
			return 0
		if s <= 15:
			return 1
		if s <= 17:
			return 2
		if s <= 18:
			return 3
		if s <= 19:
			return 4
		if s <= 20:
			return 5
		return 6
		
	def get_tohit_missile_mod(self):
		adj_dex = self.dexterity + self.dex_mod
		if adj_dex < 13:
			return 0
		elif adj_dex <= 15:
			return 1
		elif adj_dex <= 17:
			return 2
		elif adj_dex <= 18:
			return 3
		elif adj_dex <= 19:
			return 4
		elif adj_dex <= 20:
			return 5
		return 0
		
	def get_num_attacks(self, weapon): #per round
		level = self.get_skill_level(weapon.cat)
		if weapon.name.upper().find('BOW') != -1 and level >= 3:
			return 2
		if weapon.name.upper().find('SWORD') != -1 and level >= 5:
			return 2
		if weapon.name.upper().find('DAGGER') != -1 and self.level >= 3:
			return 2
		if weapon.name.upper().find('STAFF') != -1 and self.level >= 3:
			return 2
		elif weapon.name.upper().find('STAFF') != -1 and self.level >= 6:
			return 3
		return 1
		
	def get_pronoun_lower(self):
		if self.sex == 'male':
			return 'his'
		return 'her'
	
	def get_pronoun_capitalized(self):
		if self.sex == 'male':
			return 'His'
		return 'Her'
		
	def get_best_armor(self):
		best = None
		for item in self.inventory:
			if item.is_armor() and item.cat == SKILL_CAT_ARMOR:
				if best is None:
					best = item
				elif item.ac < best.ac:
					best = item
		return best
	
	def get_best_shield(self):
		best = None
		for item in self.inventory:
			if item.is_armor() and item.cat == SKILL_CAT_SHIELD:
				if best is None:
					best = item
				elif item.ac > best.ac:
					best = item
		return best
		
	def get_castable_non_combat_spells(self):
		spells = []
		for item in self.inventory:
			if not item.is_spell() or not self.has_skill(item.cat):
				continue
			if item.targets_environment():
				spells.append(item)
			elif item.name.upper().find("HEAL") != -1:
				spells.append(item)
			elif item.name.upper().find("BLESS") != -1:
				spells.append(item)
		return spells
		
	def update_armor_class(self):
		if not self.has_skill(SKILL_CAT_ARMOR):
			self.armor_class = 9
		else:
			best_armor = self.active_armor
			if best_armor is None:
				self.armor_class = 9
			else:
				self.armor_class = best_armor.ac
			self.armor_class -= (self.get_skill_level(SKILL_CAT_ARMOR) - 1)

		#handle magic rings and cloaks with protection
		for i in self.inventory:
			if i.is_armor() and i.name.upper().find('RING') != -1:
				self.armor_class -= i.ac
			elif i.is_armor() and i.name.upper().find('CLOAK') != -1:
				self.armor_class -= i.ac
		
		if self.has_skill(SKILL_CAT_SHIELD):
			best_shield = self.active_shield
			if best_shield:
				self.armor_class -= (self.get_skill_level(SKILL_CAT_SHIELD) * best_shield.ac)

	def get_mod_str(self, mod):
		if mod == 0:
			return " "
		if mod > 0:
			return "\t+" + str(mod)
		return '\t' + str(mod)
			
	def get_attribute_mode_strings(self):
		self.update_attribute_mods()
		ret_list = []
		ret_list.append(self.get_mod_str(self.str_mod))
		ret_list.append(self.get_mod_str(self.int_mod))
		ret_list.append(self.get_mod_str(self.wis_mod))
		ret_list.append(self.get_mod_str(self.dex_mod))
		ret_list.append(self.get_mod_str(self.con_mod))
		ret_list.append(self.get_mod_str(self.chr_mod))
		return ret_list
			
	def save(self):
		try:
			filename = self.name + '.plr'
			outfile = open(filename, "wb")
			pickle.dump(self, outfile)
			outfile.close()
			print 'Saved %s.' % self.name
		except:
			print 'Failed to save player to:', filename
			return False
		return True
		
	def load(self, name):
		loaded_player = None
		filename = name + '.plr'
		if util.DEBUG:
			infile = open(filename, "rb")
			loaded_player = pickle.load(infile)
			#print 'Loaded %s.' % loaded_player.name
			infile.close()
		else:			
			try:
				infile = open(filename, "rb")
				loaded_player = pickle.load(infile)
				#print 'Loaded %s.' % loaded_player.name
				infile.close()
			except:
				if util.DEBUG:
					print 'Failed to load player from:', filename
				return None
		
		#attempt to auto-add new class members
		try:
			t =	loaded_player.skills
			t =	loaded_player.sp
			t =	loaded_player.cur_hp
		except:
			loaded_player.sp = 4
			loaded_player.skills = []
			loaded_player.cur_hp = self.hp
		try:
			t = loaded_player.mana
			t = loaded_player.disabled
		except:				
			loaded_player.mana = 0
			loaded_player.disabled = 0
			loaded_player.gp = loaded_player.gold
			loaded_player.cp = loaded_player.copper
			loaded_player.sp = loaded_player.silver
		try:
			t = loaded_player.hidden
			t = loaded_player.mana_mod
		except:
			loaded_player.hidden = False
			loaded_player.update_attribute_mods()
		try:
			t = loaded_player.active_shield
		except:
			loaded_player.active_shield = None
			
		try:
			t = loaded_player.constitution
		except:
			loaded_player.constitution = loaded_player.constition
		try:
			t = loaded_player.personality
		except:
			loaded_player.init_personality()
			
		
		loaded_player.post_load()
		return loaded_player
		
	def post_load(self):
		self.update_armor_class()
		
	def init_personality(self):
		self.personality = []
		self.traits = []
		num_pos = random.randint(1, 2)
		for i in range(0, num_pos):
			get_random_trait(True, self.personality)
		num_neg = random.randint(1, 2)
		for i in range(0, num_neg):
			get_random_trait(False, self.personality)
		for p in self.personality:
			self.traits.append(TRAIT(p))
		
	def get_tohit_mod(self):
		if util.DEBUG:
			return 20
		if self.is_blessed():
			return 1
		return 0
	
	def get_ac(self):
		self.update_attribute_mods()
		self.update_armor_class()
		return self.armor_class + self.ac_mod
		
	def is_disabled(self):
		try:
			if self.disabled > 0:
				return True
		except:
			pass
		return False
	
	def is_trapped(self):
		try:
			if self.trapped is not None:
				return True
		except:
			pass
		return False
		
	def get_trapped_desc(self):
		try:
			return self.name + self.trapped[0]
		except:
			return '%s is not trapped.' % self.name
			
	def get_trapped_room_name(self):
		try:
			return self.trapped[1]
		except:
			return 'none'
			
	def is_blessed(self):
		try:
			if self.blessed > 0:
				return True
		except:
			pass
		return False
		
	def on_combat_end(self):
		self.magic_shield = 0
		self.disabled = 0
		self.hidden = 0
		self.blessed = 0
		self.update_attribute_mods()
		if not self.is_alive():
			print self.name, 'is damaged mortally, and in dire need of a high priest.'
		
	
	def on_combat_round_ended(self):
		if self.has('Ring of Regeneration'):
			if self.cur_hp < self.hp:
				self.cur_hp += 1
		try:
			if self.magic_shield > 0:
				self.magic_shield -= 1
		except:
			pass
		try:
			if self.disabled > 0:
				self.disabled -= 1
		except:
			pass
		try:
			if self.blessed > 0:
				self.blessed -= 1
		except:
			pass
		self.update_attribute_mods()
		
	def get_num_food_drink(self):
		num_food = 0
		num_drink = 0
		for item in self.inventory:
			if item.is_food():
				num_food += 1
			elif item.is_drink():
				num_drink += 1
		return [num_food, num_drink]
		
	def show_inventory(self):
		num_food = 0
		num_drink = 0
		for item in self.inventory:
			if item.is_food():
				num_food += 1
			elif item.is_drink():
				num_drink += 1
			else:
				print ' %s,' % item.name, item.description
		
		if num_food > 0:
			print ' food x', num_food
		if num_drink > 0:
			print ' drink x', num_drink
		
	def show(self):
		mod_list = self.get_attribute_mode_strings()
		self.update_armor_class()
		print '--------------------------------------'
		print ' Player:', self.name
		print
		print '  hp:', self.hp + (self.hp_mod * self.level), 'ac:', self.get_ac(), 'mana:', self.mana, 'xp:', self.experience, 'level:', self.level
		print '  current hp:', self.cur_hp, 'current mana:', self.cur_mana
		print 
		print '  strength:\t', self.strength, mod_list[0]
		print '  intelligence:\t', self.intelligence, mod_list[1]
		print '  wisdom:\t', self.wisdom, mod_list[2]
		print '  dexterity:\t', self.dexterity, mod_list[3]
		print '  constitution:\t', self.constitution, mod_list[4]
		print '  charisma:\t', self.charisma, mod_list[5]
		print
		print '  alignment:\t', self.alignment
		print '  race:\t\t', self.race
		print '  sex:\t\t', self.sex
		print '  age:\t\t', self.age
		print
		#print ' inventory:'
		#self.show_inventory()
		
		if self.active_weapon:
			print '  active weapon:', self.active_weapon.name
		if self.active_armor:
			print '  active armor:', self.active_armor.name
		if self.active_shield:
			print '  active shield:', self.active_shield.name
		#print '  active items:', self.active_items
		print
		print ' skill pts:', self.sp
		print ' skills:'
		for s in self.skills:
			print " ", s.name, 'level', s.level
		print
		print '  gold:', self.gp
		print
		if self.is_trapped():
			print '  description:', self.get_trapped_desc()
		else:
			print '  description:', self.description
		print '  personality traits:', self.personality
		print '  history:', self.history
		print '--------------------------------------'

		
	def add(self, item):
		if item.description[-1] != '.':
			item.description += '.'
		self.inventory.append(item)

	def activate(self, item):
		if not self.has_skill(item.cat):
			print self.name, 'needs %s training to use a %s.' % (get_skill_str(item.cat), item.name)
			return
		if item.is_weapon():
			if self.active_shield is not None and item.is_two_handed():
				print "You can't use a two handed weapon while using a shield."
				print 'Putting away shield.'
				self.active_shield = None
			self.active_weapon = item
		elif item.is_armor() and item.cat == SKILL_CAT_ARMOR:
			self.active_armor = item
		elif item.is_armor() and item.cat == SKILL_CAT_SHIELD:
			if self.active_weapon is not None and self.active_weapon.is_two_handed():
				print "You can't use a shield while holding a two handed weapon."
				return
			self.active_shield = item
		else:
			self.active_items.append(item)
		self.update_armor_class()
	
	def deactivate(self, item):
		if self.active_weapon is not None and self.active_weapon.name == item.name:
			self.active_weapon = None
		elif self.active_armor is not None and self.active_armor.name == item.name:
			self.active_armor = None
		elif self.active_shield is not None and self.active_shield.name == item.name:
			self.active_shield = None
		else:
			self.active_items.remove(item)
		self.update_armor_class()
			
	def remove(self, name):
		removed_item = None
		for i in self.inventory:
			if i.name == name:
				item = i
				self.inventory.remove(i)
				removed_item = item
				break
		#update the active items in case we just removed our last instance of it
		if removed_item is not None:
			if self.active_weapon is not None and not self.has(self.active_weapon.name):
				self.active_weapon = None
			if self.active_armor is not None and not self.has(self.active_armor.name):
				self.active_armor = None
			if self.active_shield is not None and not self.has(self.active_shield.name):
				self.active_shield = None
			for item in self.active_items:
				if not self.has(item.name):
					self.active_items.remove(item)
		return removed_item
		
	def has(self, name):
		for i in self.inventory:
			if i.name == name:
				return True
		return False
		
	def has_skill(self, cat):
		if cat == SKILL_CAT_ANY:
			return True
		for skill in self.skills:
			if skill.cat == cat:
				return True
		if util.DEBUG:
			print 'Adding skills required for this activity. DEBUG only!', get_skill_str(cat)
			self.add_skill(cat)
			return True			
		return False
		
	def add_skill(self, cat):
		self.skills.append(new_skill(cat))
		
	def get_skill_level(self, cat):
		if cat == SKILL_CAT_ANY:
			return 0
		for skill in self.skills:
			if skill.cat == cat:
				return skill.level
		return 0
		
	def get_skill(self, cat):
		for skill in self.skills:
			if skill.cat == cat:
				return skill
		return None
		
	def has_stealth_skills(self):
		return self.has_skill(SKILL_CAT_STEALTH)
		
	def set_hidden(self, val):
		self.hidden = val
		
	def can_hide(self):
		if not self.has_stealth_skills():
			return False
		if(self.active_armor is not None and self.active_armor.name.find('Leather') == -1) and self.active_armor.description.find('magic') != -1 :
			return False
		return True
		
	def get_hide_roll_thresh(self):
		return 15 - self.get_skill_level(SKILL_CAT_STEALTH)
	
	def get_pick_pocket_roll_thresh(self):
		return 10 - self.get_skill_level(SKILL_CAT_PICK_POCKET)
		
	def is_wearing_non_magic_armor(self):
		if self.active_armor is not None and self.active_armor.description.find('magic') == -1:
			return True
		return False
		
	def is_hidden(self):
		return self.hidden
	
	def is_alive(self):
		return self.cur_hp > 0
		
	def fully_healed(self):
		self.cur_hp = self.hp + (self.hp_mod * self.level)
		self.cur_mana = self.mana
		
	def is_fully_healed(self):
		return (self.cur_hp == self.hp + (self.hp_mod * self.level)) and (self.cur_mana == self.mana)
		
	def get_food(self):
		for i in self.inventory:
			if i.is_food():
				return i
		return None
	
	def get_drink(self):
		for i in self.inventory:
			if i.is_drink():
				return i
		return None
		
	def has_potions(self):
		for i in self.inventory:
			if i.is_potion():
				return True
		return False
	
	def has_scrolls(self):
		for i in self.inventory:
			if i.is_scroll():
				return True
		return False
		
	def has_wands(self):
		for i in self.inventory:
			if i.is_wand():
				return True
		return False
		
	def get_potions(self):
		potions = []
		for i in self.inventory:
			if i.is_potion():
				potions.append(i)
		return potions
		
	def get_scrolls(self):
		scrolls = []
		for i in self.inventory:
			if i.is_scroll():
				scrolls.append(i)
		return scrolls
		
	def get_wands(self):
		wands = []
		for i in self.inventory:
			if i.is_wand():
				wands.append(i)
		return wands
		
	def drink_potion(self):
		potions = self.get_potions()
		if len(potions) == 0:
			print 'no potions to drink.'
			return False
		potion = self.choose_item(potions)
		if potion is not None:
			potion.drink(self)
			self.remove(potion.name)
	
	def read_scroll(self, enemies, friends, room, level):
		scrolls = self.get_scrolls()
		if len(scrolls) == 0:
			print 'no scrolls to use.'
			return False
		scroll = self.choose_item(scrolls)
		if scroll is not None:
			if scroll.targets_environment():
				scroll.cast_at_environ( self, enemies, friends, room, level)
			else:
				scroll.cast(self, enemies, friends)
			self.remove(scroll.name)
			print 'The scroll collapses into dust.'
			
	def use_wand(self, enemies, friends, room, level):
		wands = self.get_wands()
		if len(wands) == 0:
			print 'no scrolls to use.'
			return False
		wand = self.choose_item(wands)
		if wand is not None:
			if wand.targets_environment():
				wand.cast_at_environ( self, enemies, friends, room, level)
			else:
				wand.cast(self, enemies, friends)
		
	def choose_item(self, inven, allow_cancel=True):
		t = PrettyTable(['sel', 'item', 'description'])
		if allow_cancel:
			t.add_row([0, 'cancel', ' '])
		i = 1
		for item in inven:
			t.add_row( [ i, item.name, item.description ] )
			i = i + 1
		print t.get_string(hrules=HEADER)
		valid = False
		while not valid:
			try:
				s = util.get_input("Enter the item number -> ")
				item_num = int(s) - 1
				if allow_cancel and item_num == -1:
					return None
				if item_num >= 0 and item_num < len(inven):
					valid = True
			except:
				print 'not a valid number. try again.'
				
		return inven[item_num]
		
	def rest(self):
		if self.has('Ring of Regeneration'):
			print self.name, 'uses', self.get_pronoun_lower(), 'Ring of Regeneration and recovers quickly.'
			self.fully_healed()
		elif not self.is_alive():
			print self.name, 'is damaged mortally. Rest recovers little.'
		elif self.has('Flask of Plenty'):
			print self.name, 'uses', self.get_pronoun_lower(), 'Flask of Plenty and rests well.'
			self.fully_healed()
		elif not self.is_fully_healed():
			if self.get_food() is None or self.get_drink() is None:
				print self.name, 'rests, but can not recover well without food and water.'
			else:
				self.remove(self.get_food().name)
				self.remove(self.get_drink().name)
				self.fully_healed()
		self.hidden = False
		self.magic_shield = 0
		self.disabled = 0
		self.blessed = 0
				
	def add_xp(self, reward, silent=False):
		if util.DEBUG:
			return
		if not silent:
			print self.name, 'is awarded', reward, 'xp.'
		self.experience += reward
		if self.experience > self.xp_for_next_level():
			self.level += 1
			self.sp += 4
			hp_add = random.randint(4, 8)
			self.hp += hp_add
			print self.name, 'has achieved level', self.level, '!!!'
			print 'Hp improved by %d.' % hp_add
			print 'And 4 more skill points to spend!'
			self.update_attribute_mods()
			util.pause()
			util.pause()
			
	def xp_for_next_level(self):
		if self.level == 1:
			return 1000
		if self.level == 2:
			return 2500
		if self.level == 3:
			return 4000
		if self.level == 4:
			return 8000
		if self.level == 5:
			return 18000
		if self.level == 6:
			return 35000
		if self.level == 7:
			return 75000
		if self.level == 8:
			return 125000
		if self.level == 9:
			return 250000
		if self.level == 10:
			return 500000
		if self.level == 11:
			return 7500000
		
class GoodNPC(Player):

	def roll_attr(self):
		pe = player_editor.PlayerEditor(all_skills)
		pe.set_player(self)
		pe.roll_attr()
	
