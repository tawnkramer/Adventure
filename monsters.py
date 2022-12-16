import random, copy, util
import commentary

def all_dead(group):
	for p in group:
		if p.is_alive():
			return False
	return True

class MonsterAttack(object):
	def __init__(self, usage_desc, damage):
		self.name = usage_desc
		self.usage_desc = usage_desc
		self.damage = damage
		
	def attack_target(self, monster, target, target_action, tohit_mod):
		tohit = random.randint(1, 20) + tohit_mod
		
		#for every 8 HP, we give the monster another level of ability.
		abil_mod = (monster.hp / 8)
		
		if tohit > 20:
			tohit = 20
		elif tohit < 1:
			tohit = 1
			
		if tohit == 20:
			print(monster.name, 'rolls %d! Perfect blow, double dammage!!' % tohit)
		else:
			print(monster.name, 'rolls %d.' % tohit)
		
		if tohit != 20 and tohit + abil_mod < 19 - target.get_ac() :
			i = random.randint(1, 8)
			if tohit > 14 and target.active_armor != None:
				print(monster.name, self.usage_desc, 'but', target.name, 'was saved by %s %s.' % ( target.get_pronoun_lower(), target.active_armor.name))
			elif tohit > 11 and target.active_shield != None:
				print(monster.name, self.usage_desc, 'but', target.name, 'blocked with %s %s.' % ( target.get_pronoun_lower(), target.active_shield.name))
			elif tohit > 11 and target.active_weapon != None:
				print(monster.name, self.usage_desc, 'but', target.name, 'paried with %s %s.' % ( target.get_pronoun_lower(), target.active_weapon.name))
			elif tohit < 5:
				print(monster.name, 'considers running, eyes wide with fear.')
			elif i == 1:
				print(monster.name, self.usage_desc, 'but', target.name, 'ducked just in time.')
			elif i == 2:
				print(monster.name, 'flailed uselessly at %s.' % target.name)
			elif i == 3:
				print(monster.name, self.usage_desc, 'and stumbled while attacking %s.' % target.name)
			elif i == 4:
				print(monster.name, self.usage_desc, 'but', target.name, 'dodged expertly.')
			elif i == 5:
				print(monster.name, self.usage_desc, 'but', target.name, 'avoided it.')
			elif i == 6:
				print(monster.name, self.usage_desc, 'at', target.name, 'but missed.')
			elif i == 7:
				print(monster.name, 'charges but can not hit %s.' % target.name)
			elif i == 8:
				print(monster.name, 'attacks but %s sidesteps adroitly.' % target.name)
			util.pause()
			return
		d = random.randint(1, self.damage)
		if tohit == 20:
			d = d * 2
		if target_action is not None and target_action.is_combat_action() and target_action.name == 'block':
			blocked_damage = 1 + target.dex_mod + target.level
			d -= blocked_damage
			if d < 0:
				d = 0
			else:
				print(target.name, 'blocked', blocked_damage, 'damage.')
		
		if d > 0:
			#HACK! Second chance code. Take players to 1 hp to give them a chance to run.
			#on the second attack, you will be at 1, then it's all over. So two attacks might do it.
			#still, this is something to help them out.
			narrow_miss = False
			if target.cur_hp > 1 and d >= target.cur_hp:
				d = target.cur_hp - 1
				narrow_miss = True
			
			print(monster.name, self.usage_desc, target.name, 'for', d, 'damage.')
			if narrow_miss:
				pronoun = target.get_pronoun_lower()
				print(target.name, 'narrowly escaped with %s life!' % pronoun)
			elif d > (target.hp / 2):
				print(target.name, 'is reeling from the terrible blow.')
			elif target.cur_hp < 5:
				print(target.name, 'staggers, barely keeping %s feet.' % target.get_pronoun_lower())
			elif d < 4:
				print(target.name, 'shrugs off the blow.')
			elif d < 6:
				print(target.name, 'grimaces in pain.')
			elif d < 10:
				print(target.name, 'howls in pain.')
			elif d < 15:
				print(target.name, 'shrieks in pain.')
			util.pause()
			
		target.cur_hp -= d
		if target.cur_hp < 0:
			target.cur_hp = 0
		if target.cur_hp == 0:
			print(target.name, 'has fallen!!!')
			util.pause()
		
class Monster(object):
	def __init__(self, name, description, hp, attacks, xp_award, no_appearing=1, ac=6):
		self.name = name
		self.description = description
		self.hp = hp
		self.cur_hp = hp
		self.attacks = attacks
		self.disabled = 0
		self.xp_award = xp_award
		self.no_appearing = no_appearing
		self.action_responses = []
		self.ac = ac
		self.disabled = 0
		
	def get_ac(self):
		try:
			if self.magic_shield > 0:
				return 0
		except:
			pass
		try:
			return self.ac
		except:
			pass
		return 6
		
	def get_level(self):
		return self.hp / 10
		
	def is_disabled(self):
		try:
			if self.disabled > 0:
				return True
		except:
			pass
		return False
		
	def choose_target(self, attack, players, player_actions):
		if len(players) == 0 or all_dead(players):
			return [None, None, None]
		iPlayer = random.randint(0, len(players) - 1)
		while not players[iPlayer].is_alive():
			iPlayer = random.randint(0, len(players) - 1)	
		return [ attack, players[iPlayer], player_actions[iPlayer] ]
		
	def take_combat_turn(self, players, player_actions, room, level, tohit_mod):
		if self.is_alive() and not self.is_disabled():
			for attack in self.attacks:
				action, target, target_action = self.choose_target(attack, players, player_actions)
				if action is not None:
					action.attack_target(self, target, target_action, tohit_mod)
					if not target.is_alive():
						level.combat_stats.just_died = target
						level.combat_stats.players_died.append(target)
						commentary.print_comment([commentary.DIED], players, room, level)
			return action
		return None
		
	def on_combat_end(self):
		self.magic_shield = 0
		self.disabled = 0
		self.hidden = 0
		
	def on_combat_round_ended(self):
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
		
	def add_action_response(self, ar):
		self.action_responses.append(ar)
		
	def on_action(self, action_name, item, other):
		for ar in self.action_responses:
			if ar.name == action_name:
				return ar.do_response(self, item, other)
		print(self.name, 'shrugs, unsure of what', action_name, 'means.')
		
	def is_alive(self):
		return self.cur_hp > 0

class EvilNPC(Monster):
	pass

class EvilNPC(Monster):
	pass

#name, description, max hp, attacks, xp_award, no_appearing=1, ac=6	
all_monsters = [
	Monster('Dragon', "On top of the coins sits the largest red dragon you've ever seen!", 60, [ MonsterAttack('clawed', 7), MonsterAttack('spewed flames', 9) ], 200, 1, 3 ),
	Monster('Orc', "the ugliest little yellow creature squatting over a dirty pile of rags.", 6, [ MonsterAttack('hacked', 6) ], 10, 8, 6 ),
	Monster('Ogre', "a tall, sinister human-like creature stands 8 feet tall wearing animal skin clothes.", 25, [ MonsterAttack('clubbed', 10) ], 50, 6, 5 ),
	Monster('Giant Lizard', "a 6 foot long horned creature with large silver eyes.", 30, [ MonsterAttack('bit', 8), MonsterAttack('scratched', 6) ], 75, 2, 5 ),
	Monster('Goblin', "a small, human-like creature with grey skin and red eyes.", 6, [ MonsterAttack('slashed', 6) ], 10, 8, 6 ),
	Monster('Hobgoblin', "a large, human-like creature with grey skin and red eyes.", 8, [ MonsterAttack('hacked', 8) ], 15, 6, 6 ),
	Monster('Giant Bat', "a large black furry creature with leathery wings.", 12, [ MonsterAttack('bit', 4) ], 15, 6, 6 ),
	Monster('Giant Fire Beetle', "a large red insect with two glowing spots above it's eyes.", 8, [ MonsterAttack('bit', 8) ], 15, 6, 4 ),
	Monster('Giant Tiger Beetle', "a large insect with orange and black stripes.", 18, [ MonsterAttack('bit', 12) ], 30, 4, 3 ),
	Monster('Skeleton', "a skinny, wretched creature with glowing eyes.", 6, [ MonsterAttack('slashed', 6) ], 10, 12, 7 ),
	Monster('Giant Crab Spider', "a 5 foot long orange and black hairy creature.", 12, [ MonsterAttack('bit', 8) ], 20, 4, 7 ),
	Monster('Giant Black Widow Spider', "a 6 foot long black slick creature with red hourglass on the underside.", 18, [ MonsterAttack('bit', 12) ], 30, 3, 6 ),
	Monster('Giant Tarantula', "a 7 foot black hairy creature.", 24, [ MonsterAttack('bit', 8) ], 40, 3, 5 ),
	Monster('Giant Rock Python', "a giant snake with brown and green scales.", 30, [ MonsterAttack('bit', 8) ], 50, 1, 6 ),
	Monster('Bandit', "a scraggly, hooded man.", 20, [ MonsterAttack('slashed', 8) ], 30, 5, 6 ),
	Monster('Mountain Lion', "a large, short haired cat. Fast and quiet.", 20, [ MonsterAttack('bit', 6) ], 30, 2, 6 ),
	Monster('Lizard Man', "a scaled, green man with the head of a lizard.", 12, [ MonsterAttack('speared', 7) ], 20, 5, 5 ),
	Monster('Kobold', "a short, human like, scaled creature with dark rusty brown skin. It has reddish eyes and small white horns.", 3, [ MonsterAttack('clawed', 4) ], 9, 8, 7 ),
	Monster('Female Kobold', "a short, human like, scaled creature with dark rusty brown skin. It has reddish eyes and small white horns.", 2, [ MonsterAttack('clawed', 4) ], 5, 5, 7 ),
	Monster('Kobold Guard', "a short, human like, scaled creature with dark rusty brown skin. It has reddish eyes and small white horns.", 5, [ MonsterAttack('speared', 6) ], 15, 3, 5 ),
	Monster('Giant Rat', "a rodent of unusual size.", 4, [ MonsterAttack('bit', 13) ], 8, 18, 7 ),
	Monster('Goblin', "a small, human like, green skinned creature.", 4, [ MonsterAttack('speared', 6) ], 10, 6, 6 ),
	Monster('Hobgoblin', "a medium, human like, green skinned creature.", 5, [ MonsterAttack('hacked', 8) ], 15, 6, 6 ),
	Monster('Grey Ooze', "a weird slimy gooey creature.", 15, [ MonsterAttack('spewed', 8) ], 25, 3, 8 ),
	Monster('Owlbear', "a fearsome, large beast with toothy beak and large clawed paws.", 30, [ MonsterAttack('clawed', 8), MonsterAttack('snapped', 8), MonsterAttack('clawed', 8) ], 75, 2, 5 ),
	Monster('Bugbear', "Clever, little beasts.", 11, [ MonsterAttack('slashed', 8)], 25, 5, 5 ),

]

def Mon(name, optional_desc=None):
	for m in all_monsters:
		if m.name == name:
			cm = copy.deepcopy(m)
			#randomly assign hp
			cm.hp = random.randint(int(cm.hp / 2), cm.hp)
			#scale xp depending on hp
			cm.xp_award = int(float(cm.hp) / cm.cur_hp * cm.xp_award)
			cm.cur_hp = cm.hp
			if optional_desc is not None:
				cm.description = optional_desc
			return cm
	print('monster', name, 'not found!')
	return None
