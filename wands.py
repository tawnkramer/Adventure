from spells import *
import util
import random, copy

class Wand(Spell):

	def __init__(self, name, description, location=None, cost = None, damage = None, duration = None):
		super(Wand, self).__init__(name=name, description=description, cost=cost, damage=damage, mana=0, cat=0, duration=duration)
		self.location = location
		self.charges = random.randint(3, 10)

	def is_spell(self):
		return False

	def is_wand(self):
		return True
		
	def targets_group(self):
		return True
		
	def get_skill_level(self):
		return random.randint(3, 6)
		
	def use_charge(self, caster):
		self.charges -= 1
		if self.charges <= 0:
			print("The wand's energy has run out! It vanishes in a poof!")
			caster.inventory.remove(self)

class WandOfParalyzation(Wand):
	
	def cast(self, caster, enemies, friends):
		print('Who to target with paralyzation?')
		target = self.choose_target(enemies)
		if target is None:
			return
		target.disabled = 10
		print('%s suddenly freezes completely, eyes wide with surpise.' % target.name)
		self.use_charge(caster)
			