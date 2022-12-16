'''
Callbacks from events in rooms
'''
import random
import util

class ActionResponse(object):
	def __init__(self, name, reply_fn):
		self.name = name
		self.response = reply_fn
		
	def do_response(self, reciever, actor):
		return self.response(reciever, actor)

		
#derive from RoomTrigger and pass into the room actions
#in order to wait until these events to trigger some action.
class RoomTrigger(object):

	def do_trigger_on_enter(self, room, party, level):
		return False
		
	def do_trigger_on_look(self, room, party, level):
		return False

	def do_trigger_on_fight(self, room, party, level):
		return False
	
	def do_trigger_on_won(self, room, party, level):
		return False
	
	def do_trigger_on_died(self, room, party, level):
		return False

	def do_trigger_on_run(self, room, party, level):
		return False

	def do_trigger_on_monsters_dead(self, room, party, level):
		return False
		
	def do_trigger_on_search(self, room, party, level):
		return False
	
	def do_trigger_on_loud_noise(self, room, party, level):
		return False
		
	#when this returns true, it will put the party into a combat state.
	def do_trigger_fight(self, room, party, level):
		return False
		
	#return True to remove the trigger from firing again.
	def on_triggered(self, room, party, level):
		return True

#derive from the QueryResponse class and pass into the room
#in order to trigger questions for your party.
#These questions only get triggered when we enter the room.
class QueryResponse(RoomTrigger):
		
	def query(self):
		return 'Ask a question'
		
	def response(self, reply, party):
		return True
			
	def do_trigger_on_enter(self, room, party, level):
		return True

	def on_triggered(self, room, party, level):
		q = self.query()
		reply = util.get_input(q)
		done = self.response(reply, party)
		return done
		
#this will trigger a fight. The on_triggered will return true, by default
#and then will never trigger again.
class AmbushRoomTrigger(RoomTrigger):
	def do_trigger_fight(self, room, party, level):
		util.get_input('You are ambushed! Hit return to continue.')
		return True

#this will trap and damage some of the party on enter.
#it will require a rope to get them out.
class PitfallRoomTrigger(RoomTrigger):
	def __init__(self):
		self.discovered = False
		
	def do_trigger_on_enter(self, room, party, level):
		return True
		
	def on_triggered(self, room, party, level):
		if self.discovered:
			print('Everyone steps carfeully to avoid the pitfall.')
			for p in party:
				if p.is_trapped() and p.get_trapped_room_name() == room.name:
					print(p.get_trapped_desc())
		
		if not self.discovered:
			self.discovered = True
			print('The floor is fake here. It looks like a pitfall trap!')
			any_trapped = False
			num_trapped = 0
			for p in party:
				if random.randint(1, 6) < 4:
					num_trapped += 1
					if num_trapped == len(party):
						#can't allow everyone to be trapped
						continue
					dam = random.randint(1, 6)
					print(p.name, 'falls into a hidden pit and takes %d damage!' % dam)
					p.cur_hp -= dam
					if p.cur_hp <= 0:
						p.cur_hp = 0
						print(p.name, 'collapses to the floor, unconscious.')
					p.trapped = [' is trapped in a pit in %s.' % room.name, room.name]
					any_trapped = True
			if any_trapped is False:
				print('Whew! Everyone avoided the trap!')
		if self.discovered:
			num_trapped = 0
			for p in party:
				if p.is_trapped():
					num_trapped += 1
			has_rope = None
			if num_trapped > 0:
				for p in party:
					if p.has('rope'):
						has_rope = p
						break
				if has_rope:
					print('Thankfully', p.name, 'has rope. Everyone manages to climb to safety.')
					for p in party:
						p.trapped = None
				else:
					print('If only someone had some rope, they should be able to easily rescue them.')
		return False
		
class TempleQueryResponse(QueryResponse):
	def query(self):
		return '''A golden robed high priest greets you with a slow nod. "Welcome travelers. Be at peace. You may rest here and pray as long as you like. Do you require my healing services?" (y, n) -> '''
		
	def response(self, reply, party):
		if reply == 'n':
			print('"May the blessings be yours."')
		else:
			dead = None
			for p in party:
				if not p.is_alive():
					dead = p
			if dead is None:
				print('"While you may need healing, it appears nothing that proper rest can not attain. Please be welcome, and stay."')
				return
			print('''"Ahh, I see that this one is gravely stricken." His brow furrows as he lays one hand on %s's forehead lightly. "Shall we revive the one called %s."''' % (dead.name, dead.name))
			yn = util.get_input('"A donation of 100 gp helps us to continue helping the needy. Please pledge your support. (y, n) -> "') 
			if yn == 'n':
				print('"As you wish. And all the blessing upon this one."')
				return
			if dead.constitution == 1:
				print("I'm sorry. This damaged soul is beyond my ability to help.")
				return			
			totalgp = 0
			for p in party:
				totalgp += p.gp
			if totalgp < 100:
				print('''"I see that all you can donate now is %d gp. This one is in need. Let us come to %s aid."''' % (totalgp, p.get_pronoun_lower()))
				for p in party:
					if len(p.inventory) > 0:
						print('The priest accepted', p.inventory[0].name, 'from %s.' % p.name)
						p.remove(p.inventory[0].name)
			collected = 0
			#attempt at equitable collection.
			#first from dead players
			if dead.gp > 100:
				collected = 100
				dead.gp -= collected
			else:
				collected = dead.gp
				dead.gp = 0
			#then equally among remaining
			if len(party) > 1 and collected < 100:
				remaining = 100 - collected
				share = int(remaining / (len(party) - 1))
				for p in party:
					if p.gp > share:
						collected += share
						p.gp -= share
					else:
						collected += p.gp
						p.gp = 0
			#then the rest owed, if possible
			for p in party:
				if collected < 100:
					remaining = 100 - collected
					if p.gp > remaining:
						collected += remaining
						p.gp -= remaining
					else:
						collected += p.gp
						p.gp = 0
			#now the ressurrection
			print('''
  The high priest summons his clergy. They file in silently, dressed in golden robes and align in a circle around a raised daise upon which %s rests. Heavy golden insense decanters throw a pungent smoke into the air. The priests extend their hands, palm to the sky.
			
  And the chanting begins. Quietly at first. Their voices combine and fill the great hall. Slowly the chanting deepens. Resonate frequencies combine to create ethereal harmonies, as if more unseen chanters had added their voice. The air grows thin with electricity and a vibration sets up in the floor and walls. It is as if the building itself lends it's spirit. And then, above the heart of %s, a pircing white light appears. A point at first, growing and brightening. The power of the sound shakes the floor as the light explodes in a thunderclap. Warm air rushes from the daise and throws back the hoods and long beards of the priests. 
  
  One cannot be sure, but for a moment, in the flash, a figure of light appeared, and then as quickly vanished.
  
  In the deathly silence that follows, %s slowly lifts %s head. The priest whispers and a golden glass is offered. The clergy file silently from the room.\n''' % ( dead.name, dead.name, dead.name, dead.get_pronoun_lower() ))
			dead.fully_healed()
			dead.constitution -= 1
			print(dead.name, 'permanently loses one point of constitution.')
			dead.update_attribute_mods()
		return False

