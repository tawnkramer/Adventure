from prettytable import *
from stuff import *
from triggers import *
from monsters import *
from commentary import *
from player import *
import util
import combat

#As the name implies, a barrier between two rooms. May be locked, and may have a key assigned.
class Door ( object):
	def __init__(self, desc, key=None, locked=True):
		self.locked = locked
		self.key = key
		if key is not None:
			if not isinstance(key, Item):
				raise Exception('Was expecting an item for the key to this door: "%s", not "%s"' %( desc, key))
		self.description = desc
		self.attempts = []
		
	def is_unlocked(self):
		return not self.locked

	def is_locked(self):
		return self.locked
		
	def unlock(self):
		self.locked = False
		
	def log_attempt(self, id_str):
		try:
			self.attempts.append(id_str)
		except:
			self.attempts = []
			self.attempts.append(id_str)
			
	def has_attempted(self, id_str):
		try:
			return id_str in self.attempts
		except:
			self.attempts = []
		return False
		
##Once we've saved our level, changes we make, esp fixes, don't automatically apply to the levels
##We have already saved. So this can give a mechanism to fix botched rooms after they load.
class RoomPostLoadFixer(object):
	def make_post_load_fixes(self, current_room, loaded_room):
		pass
	
##The active instance of a post load fixer. Begins as None
room_post_load_fixer = None
	
##Assign the global instance of post load room fixer
def set_post_load_room_fixer(fixer):
	global room_post_load_fixer
	room_post_load_fixer = fixer
	

'''

A Room is technically the unit for a space that you can occupy. So interiors or exteriors, it's
all the same and a room. Perhaps a better name would have been Space.
It has collected most of the actions handling code for what you can do in a non-combat
situation. Perhaps these actions could be factored out into a separate class that could
be dynamically added to the room.

'''
class Room ( object ):
	def __init__(self, name, initial_description, description, distant_view, items=[ ], monsters = [ ], room_actions = []):
		self.name = name
		self.initial_description = initial_description #seen once on first entry
		if not isinstance(initial_description, str) and not initial_description is None:
			raise Exception("\n\n You want a string assigned to your initial_description or None,\n not %s. Check room arguments for %s" % (str(initial_description), name))
		self.description = description #repeated on each entry
		if not isinstance(description, str):
			raise Exception("\n\n You want a string assigned to your description,\n not %s. Check room arguments for %s" % (str(description), name))
		self.distant_view = distant_view
		if not isinstance(distant_view, str):
			raise Exception("\n\n You want a string assigned to your distant_view,\n not %s. Check room arguments for %s" % (str(distant_view), name))
		self.been_there  = False
		self.items = items
		if not isinstance(items, list):
			raise Exception("\n\n You want a list assigned to your items,\n not %s. Check room arguments for %s" % (str(items), name))
		for i in items:
			if not isinstance(i, Item):
				raise Exception("\n\n You want a class Item assigned to your list of items,\n not %s. Check room arguments for %s" % (str(i), name))
		
		self.monsters = monsters
		if not isinstance(monsters, list):
			raise Exception("\n\n You want a list assigned to your monsters,\n not %s. Check room arguments for %s" % (str(monsters), name))
		for m in monsters:
			if not isinstance(m, Monster) and not isinstance(m, GoodNPC):
				raise Exception("\n\n You want a class Monster or NPC assigned to your list of monsters,\n not %s. Check room arguments for %s" % (str(m), name))
		#you also want to check each instance of monster to make sure
		#that we haven't added the same instance twice. If that occurs, then
		#we have a funny problem where hitting one monster damages both!
		for i in range(0, len(monsters)):
			m = monsters[i]
			for j in range(i + 1, len(monsters)):
				om = monsters[j]
				if m == om:
					raise Exception("\n\n Can't use the same monster twice.\n Check room arguments for %s" % (name))
		self.connect_rooms = dict()
		self.room_actions = room_actions
		if not isinstance(room_actions, list):
			raise Exception("\n\n You want a list assigned to your room_actions,\n not %s. Check room arguments for %s" % (str(room_actions), name))
		for q in room_actions:
			if not isinstance(q, RoomTrigger):
				raise Exception("\n\n You want a class RoomTrigger assigned to your list of room_actions,\n not %s. Check room arguments for %s" % (str(q), name))
		self.dif_scale = 0.0
		
	def connect(self, direction, other_room, door=None, force=False):
		self.connect_room(direction, other_room, door, force)
		opposite_dir = self.get_opposite(direction)
		other_room.connect_room(opposite_dir, self, door, force)
		
	def connect_room(self, direction, other_room, door=None, force=False):
		try:
			existing_room, door = self.connect_rooms[direction]
		except:
			existing_room = None
			
		if existing_room is not None and not force:
			raise Exception("\n\n A room %s is already connected to %s to the %s. Check room connections for %s" % (existing_room.name, self.name, direction, self.name) )
			
		self.connect_rooms[direction] = [other_room, door]
		
	def get_opposite(self, direction):
		if direction == "East":
			return "West"
		if direction == "West":
			return "East"
		if direction == "North":
			return "South"
		if direction == "South":
			return "North"
		return None
		
	#attempt to handle more and less powerful parties by scaling
	#the difficulty of monsters. This adjusts their HP, attack, and count.
	def scale_difficulty(self, dif, exclude_dir=None):
		try:
			s = self.dif_scale
		except:
			self.dif_scale = 0.0
			
		if self.dif_scale == 0.0:
			if util.DEBUG:
				print 'setting dif for', self.name
			self.dif_scale = dif
			if dif > 1.0 and self.num_monsters() > 0:
				mon_hp_scale = dif
				mon_damage_scale = 1.0
				mon_count_scale = 1.0
				if dif > 2.0:
					mon_hp_scale = 2.0
					mon_damage_scale = dif - 2.0
				if dif > 4.0:
					mon_damage_scale = 2.0
					mon_count_scale = dif - 4.0
				if mon_count_scale > 1.0:
					num_to_add = int(self.num_monsters() * mon_count_scale)
					m = self.monsters[-1]
					if util.DEBUG:
						print 'adding', num_to_add, m.name
					for i in range(0, num_to_add):
						nm = Mon(m.name)
						if nm is not None:
							self.monsters.append(nm)
				if mon_hp_scale > 1.0:
					for m in self.monsters:
						m.hp = int(m.hp * mon_hp_scale)
						if util.DEBUG:
							print m.name, 'hp:', m.hp
						m.cur_hp = int(m.cur_hp * mon_hp_scale)
						m.xp_award = int(m.xp_award * mon_hp_scale)  
						for a in m.attacks:
							if mon_damage_scale > 1.0:
								a.damage = int(a.damage * mon_damage_scale)
								if util.DEBUG:
									print '  dam:', a.damage
			elif dif < 1.0 and self.num_monsters() > 0:
				mon_hp_scale = dif
				mon_damage_scale = dif
				if dif < 0.5 and len(self.monsters) > 2:
					#remove some monsters
					for i in range( 2, len(self.monsters)):
						do_remove = random.randint(1, 10) > (dif * 10)
						if do_remove:
							self.monsters.pop()
						
				for m in self.monsters:
					m.hp = int(m.hp * mon_hp_scale)
					if m.hp < 1:
						m.hp = 1
					if util.DEBUG:
						print m.name, 'hp:', m.hp
					m.cur_hp = m.hp
					m.xp_award = int(m.xp_award * mon_hp_scale)  
					for a in m.attacks:
						a.damage = int(a.damage * mon_damage_scale)
						if util.DEBUG:
							print '  dam:', a.damage
				#also scale the value of items found
				for i in self.items:
					if isinstance(i, Item) and i.cost is not None:
						i.cost.count = int(i.cost.count * dif)						
			
		
		for direction in self.connect_rooms:
			if direction == exclude_dir:
				continue
			room, door = self.connect_rooms[direction]
			room.scale_difficulty(dif, self.get_opposite(direction))
	
	def all_same_type(self, monsters):
		if len(monsters) == 0:
			return True
		for m in monsters:
			if m.name != monsters[0].name:
				return False
		return True

	def look(self, party, level, show_initial=False):
		print
		if not self.been_there or show_initial:
			self.been_there = True
			if self.initial_description:
				print self.initial_description
			else:
				print self.description
		else:
			print self.description
			self.do_triggers(party, level, 'on_look')
			
		num_mon = len(self.monsters)
		if num_mon > 1:
			if self.all_same_type(self.monsters):
				print 'A group of', num_mon, '%ss are here.' % self.monsters[0].name
			elif isinstance(self.monsters[-1], EvilNPC):
				print 'A group of', num_mon, 'men are here.'
			else:
				print 'A group of', num_mon, 'monsters are here.'
			print self.monsters[0].description
		else:
			for mon in self.monsters:
				print mon.description
				
		try:
			if self.enter_comment is not None:
				print
				print self.enter_comment
				self.enter_comment = None
		except:
			pass
		
		print
		print '......'
		print
		for direction in self.connect_rooms:
			room, door = self.connect_rooms[direction]
			if door is not None:
				description = direction + " you see " + door.description 
			else:
				description = direction + " you see " + room.get_distant_view() 
			print description
		print
		
	def do_triggers(self, party, level, trigger_name):
		func_name = "do_trigger_" + trigger_name
		if util.DEBUG:
			for action in self.room_actions:
				if isinstance(action, RoomTrigger) and getattr(action, func_name)(self, party, level):
					do_remove = action.on_triggered(self, party, level)
					if(do_remove):
						self.room_actions.remove(action)
					return True
		else:
			try:
				for action in self.room_actions:
					if isinstance(action, RoomTrigger) and getattr(action, func_name)(self, party, level):
						do_remove = action.on_triggered(self, party, level)
						if(do_remove):
							self.room_actions.remove(action)
						return True
			except:
				pass
		return False
			
	def search(self, party, level):
		if not self.do_triggers(party, level, "on_search"):
			self.default_room_search(party)
		
	def default_room_search(self, party):	
		for m in self.monsters:
			if isinstance(m, GoodNPC):
				continue
			if isinstance(m, EvilNPC) and not util.DEBUG:
				print "You can't search now. %s has his evil eye on you." % m.name
				return
			if isinstance(m, Monster) and not util.DEBUG:
				print "You can't search now unless you want the monsters to eat you."
				return
		
		if len(self.items) == 0:
			print "You don't find anything interesting."
		else:
			self.dole_out_one_item(party, 'You discover', self.items)			
			
	def dole_out_one_item(self, party, action_desc, item_list):
		for item in item_list:
			if item.description and item.location:
				print action_desc, item.description, item.location
			elif item.description:
				print action_desc, item.description
			else:
				print action_desc, item.name
				
			divide_loot(party, [item])
			self.items.remove(item)
			break
	
	def get_distant_view(self):
		if isinstance(self.distant_view, str):
			return self.distant_view
		return 'a fuzzy haze.'
		
	def check_for_wandering_monsters(self):
		return #for some reason this doesn't work as expected...
		#it makes a random monster which somehow shows up in every room!
		if len(self.monsters) > 0:
			return
		roll = random.randint(1, 20)
		if roll > 3:
			return
		global all_monsters
		which = random.randint(0, len(all_monsters) - 1)
		m = all_monsters[which]
		if m.name.find('Dragon') == -1:
			mon = Mon(m.name)
			mon.description = 'A %s wandered in here. It looks like %s' % (m.name, m.description)
			self.monsters = [ mon ]			
		
	def on_enter(self, party, level, entered_from_room=None):
		print "~+----------------------------------------+~"
		print '    ', self.name
		print "~+----------------------------------------+~"
		print
		self.entered_from_room = entered_from_room
		self.check_for_wandering_monsters()
		self.look(party, level)
		self.do_triggers(party, level, "on_enter")
		
	def num_monsters(self):
		n = 0
		for m in self.monsters:
			if isinstance(m, GoodNPC):
				continue
			if isinstance(m, EvilNPC):
				continue
			if isinstance(m, Monster):
				n = n + 1
		return n
		
	def handle_door(self, door, party, room):
		if door is None or door.is_unlocked():
			return room			
		if door.is_locked():
			print 'This door is locked.'
			key_name = 'key'
			if door.key is not None:
				key_name = door.key.name
			for user in party:
				if user.has(key_name):
					use_key = util.get_input("%s, would you like to use your %s? (y, n) -> " % (user.name, key_name))
					if use_key == 'y':
						user.remove(key_name)
						door.unlock()
						return room
				if user.has_skill(SKILL_CAT_LOCK_PICK):
					if user.has('lock pick set'):
						string_id = user.name + str(user.get_skill_level(SKILL_CAT_LOCK_PICK))
						if door.has_attempted(string_id):
							continue
						do_pick = util.get_input("%s, would you like to try to pick the lock? (y, n) -> " % user.name)
						if do_pick == 'y':
							roll = random.randint(1, 20)
							door.log_attempt(string_id)
							if roll > 15 - user.get_skill_level(SKILL_CAT_LOCK_PICK):
								print 'You picked the lock!'
								util.pause()
								door.unlock()
								return room
							else:
								print "Darn! It didn't work. This lock is beyond your skill. You won't be able to attempt again until you level up your lock pick training."
					else:
						print "%s has a lock pick skill. If you had a lock pick set that would be helpful." % user.name
		return self
		
	def choose_room_to_run(self):
		try:
			if self.entered_from_room is not None:
				return self.entered_from_room
		except:
			pass
		for direction in self.connect_rooms:
			room, door = self.connect_rooms[direction]
			if door is None or door.is_unlocked():
				return room
		return self
		
	def generate_treasure(self, party, level, monsters):
		treasure = []
		try:
			if self.no_gold:
				gold = 0
		except:
			gold = self.calc_gold()
			treasure = [GP(gold)]
		if random.randint(1, 3) < 3:
			item = self.get_random_item( all_items )
			treasure.append(item)
		if random.randint(1, 3) < 2:
			item = self.get_random_item( all_weapons )
			treasure.append(item)
		return treasure
		
	def get_random_item(self, item_list):
		while True:
			rand_item = random.randint(0, len(item_list) - 1)
			#lets make the truly expensive items deliberate, not randomly found in
			#some small orc's lair!
			if item_list[rand_item].cost.count >= 100:
				continue
			item = copy.deepcopy( item_list[rand_item] )
			break
		return item
	
	def fight(self, party, level, mon_attack_first=False):
		if len(self.monsters) == 0:
			print 'No one to fight here.'
		else:
			self.do_triggers(party, level, 'on_fight')
			result = combat.fight(party, self.monsters, self, level, mon_attack_first)
			if result == "won":
				self.do_triggers(party, level, 'on_won')
				treasure = self.generate_treasure(party, level, self.monsters)
				divide_loot(party, treasure)
				self.monsters = [] #all defeated
				self.do_triggers(party, level, 'on_monsters_dead')
				
			elif result == "died":
				self.do_triggers(party, level, 'on_died')
				return None
			elif result == "run":
				self.do_triggers(party, level, 'on_run')
				next_rm = self.choose_room_to_run()
				sitch = [RETREATED]
				next_rm.enter_comment = get_comment(sitch, party, self, level)
				#remove dead monsters from the room
				dead = []
				for m in self.monsters:
					if not m.is_alive():
						dead.append(m)
				self.monsters = util.delete__by_values(self.monsters, dead)
				return next_rm
		return self
		
	def rest(self, party, level):
		for m in self.monsters:
			if isinstance(m, GoodNPC):
				continue
			if isinstance(m, EvilNPC):
				print "You can't rest now. %s might steal your gold." % m.name
				return
			if isinstance(m, Monster):
				print "You can't rest with monsters in your bed!"
				return
		print 'You find a comfortable rock and rest your head. Hours flash by in a minute and you awake refreshed.'
		for p in party:
			p.rest()
			
	def show_inventory(self, party):
		for user in party:
			print "%s's Inventory: " % user.name 
			user.show_inventory()
			print user.cur_hp, 'hp', user.gp, 'gp'
			print
			
	def who_has(self, party, item_name):
		who = []
		for p in party:
			if p.has(item_name):
				who.append(p)
		return who
		
	def get_player(self, party, name):
		for p in party:
			if p.name == name:
				return p
		return None
		
	def show(self, party, command):
		parts = command.split(' ')
		to_show = None
		if len(parts) != 2:
			print 'Choose player to show'
			to_show = self.choose_player(party)
		else:
			to_show = self.get_player(party, parts[1])
			if to_show is None:
				print "Couldn't find a player named %s." % parts[1]
		
		if to_show:
			to_show.show()
	
	def drop(self, party, command):
		print 'Choose the player who will drop the item'
		who = self.choose_player(party)
		if who is None:
			return
		
		print 'Choose the item to drop'
		item = self.choose_item(who.inventory)
		if item is None:
			return
			
		who.remove(item.name)
		print who.name, 'dropped the %s.' % item.name
		item.location = 'right where you hid it.'
		if item.description[-1] == '.':
			item.description = item.description[:-1]
		self.items.append(item)
		
	def edit_player(self, party, command):
		to_edit = None
		parts = command.split(' ')
		if len(parts) != 2:
			print 'Choose player to edit'
			to_edit = self.choose_player(party)
		else:
			to_edit = self.get_player(party, parts[1])
			if to_edit is None:
				print "Couldn't find a player named %s." % parts[1]

		try:
			if to_edit is None:
				return
			if isinstance(to_edit, GoodNPC):
				print "Sorry, you can't edit guest members of your party."
				return
			ed = player_editor.PlayerEditor(all_skills)
			ed.do_edit(to_edit, False)
		except:
			pass
		util.clear_screen()
			
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
		
	def choose_player(self, plist, allow_cancel=True):
		t = PrettyTable(['sel', 'name'])
		i = 1
		if allow_cancel:
			t.add_row( [0, 'cancel'] )
		for p in plist:
			t.add_row( [ i, p.name ] )
			i += 1
		print t.get_string(hrules=HEADER)
		valid = False
		while not valid:
			try:
				s = util.get_input("Enter the sel number -> ")
				p_num = int(s) - 1
				if allow_cancel and p_num == -1:
					return None
				if p_num >= 0 and p_num < len(plist):
					valid = True
			except:
				print 'not a valid number. try again.'
		return plist[p_num]
	
	def read(self, party, level):
		if self.num_monsters() != 0:
			print "Can't cast spells unless you want to start a fight!"
			return
		
		print 'Choose the player who will read a scroll'
		caster = self.choose_player(party)
		if caster is None or not caster.is_alive():
			return

		scrolls = caster.get_scrolls()
		if len(scrolls) == 0:
			print caster.name, "doesn't have any scrolls."
			return
			
		print 'Choose scroll'
		scroll = self.choose_item(scrolls)
		if scroll is None:
			return
		if scroll.targets_environment():
			scroll.cast_at_environ(caster, [], party, self, level)
		elif scroll.targets_group():
			scroll.cast(caster, [], party)
		else:
			print 'Choose target'
			target = self.choose_player(party)
			if target is None:
				return
			scroll.cast_at_target(caster, target)
	
	def drink(self, party, level):		
		print 'Choose the player who will drink a potion'
		caster = self.choose_player(party)
		if caster is None or not caster.is_alive():
			return						
		caster.drink_potion()
		
	def cast(self, party, level):
		if self.num_monsters() != 0:
			print "Can't cast spells unless you want to start a fight!"
			return
		
		print 'Choose the player who will cast the spell'
		caster = self.choose_player(party)
		if caster is None or not caster.is_alive():
			return

		spells = caster.get_castable_non_combat_spells()
		if len(spells) == 0:
			print caster.name, "doesn't have any spells they can use here."
			return
			
		print 'Choose spell.'
		spell = self.choose_item(spells)
		if spell is None:
			return
		
		if spell.mana > caster.cur_mana:
			print caster.name, "doesn't have enough mana to cast that."
			return
		
		caster.cur_mana -= spell.mana
		if spell.targets_environment():
			spell.cast_at_environ(caster, None, party, self, level)
		elif spell.targets_group():
			spell.cast(caster, None, party)
		else:
			print 'Choose target'
			target = self.choose_player(party)
			if target is None:
				return
		
			spell.cast_at_target(caster, target)
			
	def calc_gold(self):
		total_hp = 0
		for m in self.monsters:
			total_hp += m.hp
		gp = random.randint(total_hp / 2, total_hp)
		return gp

	def steal(self, party, level):
		thief = None
		#first see if we can auto choose who will steal
		#you may need need the skill, or you may have an invisibility potion
		auto_pick = True
		for p in party:
			if p.is_hidden() or (p.has_skill(SKILL_CAT_STEALTH) and p.has_skill(SKILL_CAT_PICK_POCKET)):
				if thief is None:
					thief = p
				else:
					auto_pick = False
		if auto_pick and thief is None:
			print "It doesn't look like anyone in your party has the skills for this. Stealth and Pick Pocket are required."
			return self

		if not auto_pick or thief is None:
			print 'Choose the player who will attempt to steal:'
			thief = self.choose_player(party)
			if thief is None:
				return self
		
		if not thief.has_skill(SKILL_CAT_STEALTH) and not thief.is_hidden():
			print thief.name, "doesn't have any stealth skill."
			return self
		
		if not thief.has_skill(SKILL_CAT_PICK_POCKET) and not thief.is_hidden():
			print thief.name, "doesn't have any pick pocket skill."
			return self
		
		if len(self.monsters) == 0:
			print "There's no one to steal from here. You can just search."
			return self

		if not thief.can_hide() and not thief.is_hidden():
			print "You can't be stealthy in anything more than leather armor unless it's magic."
			return self

		if not thief.is_hidden():
			print thief.name, 'will attempt to hide first.'
			roll = random.randint(1, 20)
			print "You roll", roll
			if roll > thief.get_hide_roll_thresh():
				print thief.name, 'slipped into the shadows.'
			else:
				print thief.name, 'got caught trying to hide!'
				util.pause()
				return self.fight(party, level)
		print thief.name, 'attempts to steal.'
		roll = random.randint(1, 20)
		print "You roll", roll
		if roll < thief.get_pick_pocket_roll_thresh():
			print thief.name, 'got caught stealing!'
			util.pause()
			return self.fight(party, level, True)
		if len(self.items) > 0:
			print 'Choose item to steal'
			item = self.choose_item(self.items)
			if item is None:
				return self
			self.items.remove(item)
			if item.description[-1] == '.':
				item.description = item.description[:-1]
			print thief.name, 'stole %s!!' % item.description
			thief.add(item)
			return self
			
		try:
			if self.no_gold:
				print 'No gold to steal!'
				return self
		except:
			pass

		#calculate gold
		gp = self.calc_gold()
		print thief.name, 'stole %d gp!!!' % (gp)
		thief.gp += gp
		thief.add_xp(gp)
		self.no_gold = True
		return self

	def activate(self, party):
		if len(party) == 1:
			player = party[0]
		else:
			print 'Choose a player'
			player = self.choose_player(party)
		if player is None:
			return
		
		activatable = []
		for item in player.inventory:
			if item.is_weapon() or item.is_armor():
				activatable.append(item)
		if len(activatable) == 0:
			return
		print 'Choose the item to wear or equip'
		item = self.choose_item(activatable)
		if item is None:
			return
		player.activate(item)
		
	def give(self, party, command):
		if len(party) < 2:
			print 'Must have a least two people in party to give items'
			return
			
		print 'Choose the player who will give the item'
		giver = self.choose_player(party)
		if giver is None:
			return
		
		print 'Choose the item to give'
		item = self.choose_item(giver.inventory)
		if item is None:
			return
		
		if item.is_spell():
			print "Spells can't be given away or sold. They are embeded in your spell book."
			return
		
		print 'Choose the player to give the', item.name, 'to.'
		reciever = self.choose_player(party)
		if reciever is None or reciever is giver:
			return
		
		prompt = 'Are you sure %s wants to give the %s to %s?' % (giver.name, item.name, reciever.name)
		yn = util.get_input('%s (y, n) -> ' % prompt)
		if yn == 'y':
			rem = giver.remove(item.name)
			print giver.name, 'gave the %s to %s.' % (item.name, reciever.name)
			reciever.add(rem)
			reciever.on_action('give', rem, giver)
			
	def walk(self):
		room_list = []
		self.get_visited_rooms(room_list)
		room_list.remove(self)
		if len(room_list) == 0:
			print "You can fast walk to places once you have visited them."
			return self
		print
		print ("Places you have visited:")
		print
		t = PrettyTable(['sel', 'name'])
		i = 1
		for r in room_list:
			t.add_row([i, r.name])
			i = i + 1
		print t.get_string(hrules=HEADER)
		print
		valid = False
		while not valid:
			try:
				sel = util.get_input('Enter the number of place to walk to, 0 to cancel -> ')
				iSel = int(sel) - 1
				if iSel < len(room_list) and iSel >= 0:
					return room_list[iSel]
				if iSel == -1:
					valid = True
			except:
				print 'not a valid number. try again.'
		return self
		
	def handle_move_dir(self, direction, party):
		room, door = self.connect_rooms[direction]
		#can only cross an empty room
		if self.num_monsters() > 0 and room != self.entered_from_room and not util.DEBUG:
			print "Can't cross with monsters here!"
			return self
		#see if there is not door or we can pass
		return self.handle_door(door, party, room)
	
	def update(self, party, level):
		if util.DEBUG:
			for action in self.room_actions:
				if isinstance(action, RoomTrigger) and action.do_trigger_fight(self, party, level):
					do_remove = action.on_triggered(self, party, level)
					if(do_remove):
						self.room_actions.remove(action)
					return self.fight(party, level, True)	
		try:
			for action in self.room_actions:
				if isinstance(action, RoomTrigger) and action.do_trigger_fight(self, party, level):
					do_remove = action.on_triggered(self, party, level)
					if(do_remove):
						self.room_actions.remove(action)
					return self.fight(party, level, True)
		except:
			if util.DEBUG:
				print "Troubles with room actions"
			
		command = util.get_input("What would you like to do? -> ")
		if len(command) < 1:
			return self
		for direction in self.connect_rooms:
			if (len(command) == 1 and direction.upper()[0] == command.upper()[0]) or (command.upper().find(direction.upper()) != -1):
				return self.handle_move_dir(direction, party)
		if command.upper().find('SEARCH') != -1:
			self.search(party, level)
		if command.upper().find('FIGHT') != -1:
			return self.fight(party, level)
		if command.upper().find('REST') != -1:
			self.rest(party, level)
		if command.upper().find('READ') != -1:
			self.read(party, level)
		if command.upper().find('DRINK') != -1:
			self.drink(party, level)
		if command.upper().find('CAST') != -1:
			self.cast(party, level)
		if command.upper().find('LOOK') != -1:
			self.look(party, level)
		if command.upper().find('SAVE') != -1:
			level.save(party, self)
		if command.upper().find('LOAD') != -1:
			loaded_level = level.load(party)
			if loaded_level is not None:
				level = loaded_level
				level.scale_difficulty(party)
				return level.current_room
		if command.upper().find('QUIT') != -1 or command.upper()[0] == 'Q':
			return None
		if command.upper().find('INVENTORY') != -1 or command.upper()[0] == 'I':
			self.show_inventory(party)
		if command.upper().find('GIVE') != -1:
			self.give(party, command)
		if command.upper().find('EDIT') != -1:
			self.edit_player(party, command)
		if command.upper().find('DROP') != -1:
			self.drop(party, command)
		if command.upper().find('SHOW') != -1:
			self.show(party, command)
		if command.upper() == 'WALK':
			return self.walk()
		if command.upper() == 'WEAR' or command.upper() == 'EQUIP':
			self.activate(party)
		if command.upper().find('HELP') != -1 or command.upper()[0] == 'H':
			self.print_help()
		if command.upper() == ('STEAL'):
			return self.steal(party, level)
		return self
		
	def print_help(self):
		print "try the commands: search, fight, rest, look, show, go 'direction', inventory, wear, equip, give, drop, walk, cast, read, drink, edit, steal, save, load, quit, help.\n\n Sometimes the first letter of the command or direction is also enough."
		
	def find_room(self, room_name, exclude_dir=None):
		if self.name == room_name:
			return self
		for direction in self.connect_rooms:
			if direction == exclude_dir:
				continue
			room, door = self.connect_rooms[direction]
			found = room.find_room(room_name, self.get_opposite(direction))
			if found is not None:
				return found
		return None
		
	def get_visited_rooms(self, room_list, exclude_dir=None):
		if self.been_there or util.DEBUG:
			room_list.append(self)
		for direction in self.connect_rooms:
			if direction == exclude_dir:
				continue
			room, door = self.connect_rooms[direction]
			room.get_visited_rooms(room_list, self.get_opposite(direction))
		
	def add_missing_rooms(self, loaded_room, exclude_dir=None):
		if self.name != loaded_room.name:
			print "Error, shouldn't be comparing rooms of different names:", self.name, loaded_room.name
			return
			
		#we could update descriptions and other info, in case there was corrections.
		#we will check a global callback function and give it a chance to process rooms
		#as they are loaded.
		global room_post_load_fixer
		if room_post_load_fixer is not None:
			room_post_load_fixer.make_post_load_fixes(self, loaded_room)
		
		#print 'comparing', self.name, 'to', loaded_room.name			
		for direction in self.connect_rooms:
			if direction == exclude_dir:
				continue
			#print 'checking dir', direction
			room, door = self.connect_rooms[direction]
			try:
				oroom, odoor = loaded_room.connect_rooms[direction]
			except:
				print 'Adding new room:', room.name
				force = True
				loaded_room.connect(direction, room, door, force)
				continue
			room.add_missing_rooms(oroom, self.get_opposite(direction))
		
	def on_exit(self):
		pass
		
def get_num_alive(party):
	n = 0
	for p in party:
		if p.is_alive() and not p.is_trapped():
			n += 1
	return n
	
def in_party(party, name):
	for p in party:
		if p.name == name:
			return True
	return False
	
def get_player(party, name):
	for p in party:
		if p.name == name:
			return p
	return None
		
def how_many_can_use(item, party):
	can_use = []
	for p in party:
		if not p.is_alive() or p.is_trapped():
			continue
		if p.has_skill(item.cat):
			can_use.append(p)
	return [len(can_use), can_use]
	
def divide_loot(party, treasure):
	num_alive = get_num_alive(party)
	if num_alive == 0:
		return
	for t in treasure:
		if isinstance(t, Coins):
			if util.DEBUG:
				continue
			share = t.count / num_alive
			for p in party:
				if p.is_alive() and share > 0:
					print p.name, 'gets', share, 'gold.'
					p.gp += share
					silent = True
					p.add_xp(share, silent)
		else:
			c, can_use = how_many_can_use(t, party)
			#after it's found, terminate descriptions with a period.
			if t.description[-1] != '.':
				t.description += '.'
			article = 'a'
			if isinstance(t, Food) or isinstance(t, Drink) or t.name == 'torches' or t.name == 'rope' or t.name[-1] == 's':
				article = 'some'
			elif t.name.upper()[0] == 'A':
				article = 'an'
			if c == 1:
				print can_use[0].name, 'finds %s %s.' % (article, t.name)
				can_use[0].add(t)
			elif c == 0 and num_alive == 1:
				for p in party:
					if p.is_alive():
						print p.name, 'finds %s %s.' % (article, t.name)
						p.add(t)
						break
			else:
				taken = False
				while not taken:
					who = util.get_input('Enter name of player who gets the %s -> ' % t.name)
					for p in party:
						if p.name == who:
							if p.is_trapped():
								print p.get_trapped_desc()
							else:
								print p.name, 'gets the %s.' % t.name
								p.add(t)
								taken = True
					if not taken:
						print 'Did not match that name', who, 'with anyone in your party.'
	

