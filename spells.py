from items import *
import copy
import random
import util

class Spell(Item):
	def __init__(self, name, description, cost, damage, mana, cat, duration = None):
		super(Spell, self).__init__(name, description, None, cost)
		self.damage = damage
		self.mana = mana
		self.cat = cat
		self.duration = duration
		
	def is_spell(self):
		return True
		
	def is_magic(self):
		return True
		
	def is_healer_cat(self):
		return (self.cat == SKILL_CAT_HEALER)
		
	def targets_group(self):
		return False
		
	def targets_environment(self):
		return False
		
	def cast(self, caster, enemies, friends):
		print 'Empty spell def - cast.'
		pass
	
	def cast_at_target(self, caster, target):
		print 'Empty spell def - cast_at_target.'
		pass
		
	def cast_at_environ(self, caster, enemies, friends, room, level):
		print 'Empty spell def - cast at environ.'
		pass
		
	def choose_target(self, targets):
		i = 1
		for p in targets:
			print i, p.name
			i = i + 1
		valid = False
		while not valid:
			try:
				sel = util.get_input('Enter sel number -> ')
				iSel = int(sel) - 1
				if iSel >= 0 and iSel < len(targets) and targets[iSel].is_alive():
					valid = True
			except:
				print 'invalid input'
		return targets[iSel]
	
class OffSpell(Spell):		
	def cast_at_target(self, caster, target):
		d = random.randint(1, self.damage) + caster.get_skill_level(self.cat)
		print caster.name, "casts", self.name, 'for', d, 'damage to', target.name
		target.cur_hp -= d
		if target.cur_hp <= 0:
			target.cur_hp = 0
			print 'The', target.name, 'slumps to the ground, motionless.'

class LevelMultOffSpell(Spell):	
	def cast_at_target(self, caster, target):
		d = random.randint(1, self.damage) * caster.get_skill_level(self.cat)
		print caster.name, "casts", self.name, 'for', d, 'damage to', target.name
		target.cur_hp -= d
		if target.cur_hp <= 0:
			target.cur_hp = 0
			print 'The', target.name, 'slumps to the ground, motionless.'

class GroupOffSpell(Spell):
	def targets_group(self):
		return True

	def cast(self, caster, enemies, friends):
		d = random.randint(1, self.damage) * caster.get_skill_level(self.cat)
		print caster.name, "casts", self.name, 'for', d, 'damage to all enemies!'
		for target in enemies:
			if target.is_alive():
				target.cur_hp -= d
				if target.cur_hp <= 0:
					target.cur_hp = 0
					print 'The', target.name, 'slumps to the ground, motionless.'
		util.pause()

class DisableSpell(Spell):
	def cast_at_target(self, caster, target):
		print caster.name, 'casts', self.name, 'on', target.name, ' disabling them for', self.duration, 'rounds.'
		target.disabled = self.duration
		
class DisableGroupSpell(Spell):
	def targets_group(self):
		return True

	def cast(self, caster, enemies, friends):
		print caster.name, 'casts', self.name, 'disabling some enemies for', self.duration, 'rounds.'
		util.pause()
		for target in enemies:
			if not target.is_alive():
				continue
			roll = random.randint(1, 20)
			if roll > (10 - caster.get_skill_level(self.cat) + target.get_level()):
				print target.name,
				if self.name == 'Light':
					print 'is blinded!'
				elif self.name == 'Sleep':
					print 'falls to the floor, asleep!'
				else:
					print 'is disabled.'			
				target.disabled = self.duration
			else:
				print target.name, 'is not affected.'
		
class ShieldSpell(Spell):
	def targets_group(self):
		return True
	
	def cast(self, caster, enemies, friends):
		caster.magic_shield = 3 * caster.get_skill_level(self.cat)
		print 'A large glowing blue sphere protects %s.' % caster.name

class InvisibilitySpell(Spell):
	def targets_group(self):
		return True
	
	def cast(self, caster, enemies, friends):
		print 'Who to target with invibility spell?'
		target = self.choose_target(friends)
		target.hidden = True
		print '%s suddenly disappears completely.' % target.name
		
class KnockSpell(Spell):
	def targets_environment(self):
		return True
	
	def cast_at_environ(self, caster, enemies, friends, room, level):
		did_unlock = False
		for direction in room.connect_rooms:
			nroom, door = room.connect_rooms[direction]
			if door is not None and not door.is_unlocked():
				door.unlock()
				print 'A red light shoots from %s to the door, blasting it open with a thunderous clap!' % caster.name
				door.description = "the charred remains of a door barely hang by the melted hinges."
				did_unlock = True
				nroom.do_triggers(friends, level, 'on_loud_noise')
				break
		if not did_unlock:
			print 'No doors to unlock here.'
		
class HealSpell(Spell):
	def targets_group(self):
		#not true, but calls cast with friends list
		return True
		
	def cast(self, caster, enemies, friends):
		print 'Who to target with healing spell?'
		target = self.choose_target(friends)
		if not target.is_alive():
			print target.name, 'is beyond your skills. They need the attention of a high priest.'
			return
		h = random.randint(1, self.damage) * caster.get_skill_level(self.cat)
		print caster.name, "casts", self.name, 'healing', h, 'damage to', target.name
		target.cur_hp += h
		#can't exceed our max hp
		if target.cur_hp > target.hp:
			target.cur_hp = target.hp

class BlessSpell(Spell):
	def targets_group(self):
		return True
		
	def cast(self, caster, enemies, friends):
		rounds = random.randint(1, caster.get_skill_level(self.cat)) + caster.get_skill_level(self.cat)
		print caster.name, "casts", self.name, 'giving everyone a radiant light and increasing strength for %d rounds.' % rounds
		for p in friends:
			if p.is_alive():
				p.blessed = rounds
		
class ScareSpell(Spell):
	def targets_group(self):
		return True
		
	def cast(self, caster, enemies, friends):
		print caster.name, "casts", self.name, 'summoning a giant glowing aura.'
		for e in enemies:
			if e.is_alive():
				roll = random.randint(1, 20)
				if roll > (10 - caster.get_skill_level(self.cat)):
					print e.name, 'runs in terror!'
					enemies.remove(e)
					util.pause()

class HealGroupSpell(Spell):
	def targets_group(self):
		return True
		
	def cast(self, caster, enemies, friends):
		print caster.name, "casts", self.name, 'summoning a giant healing aura.'
		for f in friends:
			if f.is_alive():
				h = random.randint(1, self.damage) * caster.get_skill_level(self.cat)
				f.cur_hp += h
				if f.cur_hp > f.hp:
					f.cur_hp = f.hp
					print f.name, 'is fully healed.'
				else:
					print f.name, 'heals', h, 'damage.'

class CreateFoodSpell(Spell):
	def targets_group(self):
		return True
		
	def cast(self, caster, enemies, friends):
		print 'Who to give food to?'
		target = self.choose_target(friends)
		if target is None:
			return
		units = 3 * caster.get_skill_level(self.cat)
		print target.name, 'gets', units, 'units of food and water.'
		for f in range(0, units):
			target.add(Food('bread', 'a magical loaf of bread.', None, GP(1)))
			target.add(Food('water', 'a magical flask of water.', None, GP(1)))
		
class ResurrectionSpell(Spell):
	def targets_group(self):
		return True
		
	def cast(self, caster, enemies, friends):
		print 'Who to bring back from the dead?'
		target = self.choose_target(friends)
		if target is None:
			return
		if target.is_alive():
			print target.name, 'is alive. Normal healing will be adequate. This spell does nothing for them.'
			return
		print caster.name, 'lifts', caster.get_pronoun_lower(), 'arms into the air and summons all the power of the light and good. In a blinding flash as bright as the sun, a hot wind hits everyone as the light enters %s.' % target.name
		target.fully_healed()
		print target.name, 'sits up, blinking, and smiles.'
	
class LaughSpell(Spell):
	def targets_group(self):
		return True
		
	def cast(self, caster, enemies, friends):
		target = self.choose_target(enemies)
		if target.is_alive():
			rounds = 3			
			print target.name, "falls on the floor laughing for %d rounds!" % rounds