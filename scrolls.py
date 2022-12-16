from spells import *
import util
import random, copy

class Scroll(Spell):

	def __init__(self, name, description, location=None, cost = None, damage = None, duration = None):
		super(Scroll, self).__init__(name=name, description=description, cost=cost, damage=damage, mana=0, cat=0, duration=duration)
		self.location = location

	def is_spell(self):
		return False

	def is_scroll(self):
		return True
		
	def targets_group(self):
		return True
		
	def get_skill_level(self):
		return random.randint(3, 6)
				
class InvisibilityScroll(Scroll):

	def cast(self, caster, enemies, friends):
		print('Who to target with invibility spell?')
		target = self.choose_target(friends)
		target.hidden = True
		print('%s suddenly disappears completely.' % target.name)
		
class HealScroll(Scroll):
	
	def cast(self, caster, enemies, friends):
		print('Who to target with healing spell?')
		target = self.choose_target(friends)
		if not target.is_alive():
			print(target.name, 'is beyond this magic. They need the attention of a high priest.')
			util.pause()
			return
		h = random.randint(1, 8) * self.get_skill_level()
		print(caster.name, "reads the scroll, healing", h, 'damage to', target.name)
		target.cur_hp += h
		#can't exceed our max hp
		if target.cur_hp > target.hp:
			target.cur_hp = target.hp
		util.pause()
		
class BlessScroll(Scroll):
		
	def cast(self, caster, enemies, friends):
		rounds = random.randint(1, self.get_skill_level()) + self.get_skill_level()
		print(caster.name, 'reads the scroll, giving everyone a radiant light and increasing strength for %d rounds.' % rounds)
		for p in friends:
			if p.is_alive():
				p.blessed = rounds
		util.pause()

class KnockScroll(Scroll):

	def targets_environment(self):
		return True
	
	def cast_at_environ(self, caster, enemies, friends, room, level):
		did_unlock = False
		for direction in room.connect_rooms:
			nroom, door = room.connect_rooms[direction]
			if door is not None and not door.is_unlocked():
				door.unlock()
				print('A red light shoots from %s to the door, blasting it open with a thunderous clap!' % caster.name)
				door.description = "the charred remains of a door barely hang by the melted hinges."
				did_unlock = True
				nroom.do_triggers(friends, level, 'on_loud_noise')
				break
		if not did_unlock:
			print('No doors to unlock here.')

class FireBallScroll(Scroll):

	def cast(self, caster, enemies, friends):
		d = random.randint(1, 8) * self.get_skill_level()
		print('As', caster.name, "reads the scroll, a hot wind rushes to him followed by a blast of fire shooting out and exploding for", d, 'damage to all enemies!')
		for target in enemies:
			if target.is_alive():
				target.cur_hp -= d
				if target.cur_hp <= 0:
					target.cur_hp = 0
					print('The', target.name, 'is blasted back and thrown to the ground, motionless.')
		util.pause()
