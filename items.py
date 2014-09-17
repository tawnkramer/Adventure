from skill import *
import util

COIN_GP = 'gp'
COIN_CP = 'cp'
COIN_SP = 'sp'

class Coins(object):
	def __init__(self, count, type):
		self.count = count
		self.type = type
		
	def get_str(self):
		return str(self.count) + ' ' + self.type
	
#utility functions to make construction of coins a little abbreviated	
def GP(count):
	return Coins(count, COIN_GP)
	
def CP(count):
	return Coins(count, COIN_CP)
	
def SP(count):
	return Coins(count, COIN_SP)
	
class Item(object):
	def __init__(self, name, description, location=None, cost=None, cat=SKILL_CAT_ANY):
		self.name = name
		self.description = description
		self.location = location
		self.cost = cost
		self.cat = cat
		#validation of input
		if not isinstance(name, str):
			raise Exception("Expecting a string for name for item not %s" % str(name))
		#if description is not None and not isinstance(description, str):
		if not isinstance(description, str):
			raise Exception("Expecting a string for description for item: %s, not %s" % (self.name, str(description)))
		if cost is not None and not isinstance(cost, Coins):
			raise Exception("Expecting coins for cost for item: %s, not %s" % (self.name, str(cost)))
		if not isinstance(cat, int):
			raise Exception("Expecting an integer for cat for item: %s, not %s" % (self.name, str(cat)))
		
	def is_magic(self):
		return False
		
	def is_weapon(self):
		return False
		
	def is_spell(self):
		return False
		
	def is_armor(self):
		return False
		
	def is_food(self):
		return self.name == 'bread'
		
	def is_drink(self):
		return self.name == 'water'
		
	def is_potion(self):
		return False
	
	def is_scroll(self):
		return False
		
	def is_wand(self):
		return False
	
	def is_combat_action(self):
		return False

class Food(Item):
	def is_food(self):
		return True	

class Drink(Item):
	def is_drink(self):
		return True	
		
class Weapon(Item):
	def __init__(self, name, description, damage, use_desc, cost=None, skill_cat=SKILL_CAT_ANY, location=None, hit_bonus=None, damage_bonus=None):
		super(Weapon, self).__init__(name, description, location, cost, skill_cat)
		if not isinstance(description, str):
			raise Exception('need a string description')
		self.damage = damage
		self.use_desc = use_desc #slashes, shoots, etc..
		self.hit_bonus = hit_bonus
		self.damage_bonus = damage_bonus
		
	def get_damage(self):
		d = random.randint(1, self.damage)		
		return d

	def is_two_handed(self):
		return self.name.find('Two-handed') != -1 or self.name == 'Quarterstaff' or self.name.find("Bow") != -1
		
	def get_hit_bonus(self):
		try:
			if self.hit_bonus:
				return self.hit_bonus
		except:
			pass
		return 0
	
	def get_damage_bonus(self):
		try:
			if self.damage_bonus:
				return self.damage_bonus
		except:
			pass
		return 0
		
	def is_weapon(self):
		return True
		
	def attack(self, player, enemies, friends, fatigue_tohit_mod):
		enemy = enemies[0]
		self.attack_target(player, enemy, fatigue_tohit_mod)
		
	def attack_target(self, player, target, fatigue_tohit_mod):
		num_attacks = player.get_num_attacks(self)
		for i in range(0, num_attacks):
			if not target.is_alive():
				continue 
			tohit = random.randint(1, 20) + fatigue_tohit_mod
			if tohit > 20:
				tohit = 20
			elif tohit < 1:
				tohit = 1
			if self.cat == SKILL_CAT_MISSILE:
				tohit_mod = player.get_tohit_missile_mod() + self.get_hit_bonus()
			else:
				tohit_mod = player.get_tohit_mod() + self.get_hit_bonus()
			if target.disabled > 0:
				tohit_mod += 5
			if player.is_hidden():
				tohit_mod += 10
			if tohit_mod > 0:
				print player.name, 'rolls %d (+%d).' % (tohit, tohit_mod)
			else:
				print player.name, 'rolls %d.' % tohit
			
			tohit += tohit_mod	
			if tohit != 20 and tohit < 20 - target.get_ac() - player.get_skill_level(self.cat) :
				print player.name, self.use_desc, 'at', target.name, 'but missed.'
				return
			d = random.randint(1, self.damage)
			if tohit == 20:
				print 'Perfect blow! Double damage!!'
				d = d * 2
			dm = player.get_damage_mod() + player.get_skill_level(self.cat) - 1 + self.get_damage_bonus()
			if player.is_hidden():
				print 'Suprise attack adds %d damage.' % (d + 3)
				dm += d + 3
			if target.disabled > 0:
				dm += 3
			if dm > 0:
				print player.name, self.use_desc, target.name, 'for', d, 'damage (+%d).' % dm
				d += dm			
			elif dm < 0:
				print player.name, self.use_desc, target.name, 'for', d, 'damage (%d).' % dm			
				d += dm	
			else:
				print player.name, self.use_desc, target.name, 'for', d, 'damage.'
			if d > 0:
				target.cur_hp -= d
				if target.cur_hp <= 0:
					target.cur_hp = 0
					print 'The', target.name, 'slumps to the ground, motionless.'
				elif d > (target.hp / 2):
					print target.name, 'is reeling from the terrible blow!'
				elif target.cur_hp < 5:
					print target.name, 'staggers, barely keeping their feet.'
				elif d < 3:
					print target.name, 'shrugs off the blow.'
				elif d < 5:
					print target.name, 'grimaces in pain.'
				elif d < 8:
					print target.name, 'howls in pain.'
				else:
					print target.name, 'shrieks in pain.'
				
				#getting hit snaps monster out of any magical disabled state.
				if target.disabled > 0:
					target.disabled = 0
		
	
class Armor(Item):
	def __init__(self, name, description, cost, ac, cat=SKILL_CAT_ARMOR, location=None):
		super(Armor, self).__init__(name, description, location, cost, cat)
		self.ac = ac
		
	def is_armor(self):
		return True
		
class MagicWeapon(Weapon):
	def is_magic(self):
		return True
	
class MagicArmor(Armor):
	def is_magic(self):
		return True

class MagicItem(Item):
	def is_magic(self):
		return True
		