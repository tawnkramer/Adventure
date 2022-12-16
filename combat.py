import random
from prettytable import *
from util import *
from commentary import *

HP_RECOVERED_FROM_REST = 1

class CombatStats(object):
	COMBAT_STATUS_NONE = 0
	COMBAT_STATUS_FIGHTING = 1
	COMBAT_STATUS_RAN = 2
	COMBAT_STATUS_WON = 3
	COMBAT_STATUS_ALL_DIED = 4

	def __init__(self):
		self.players_died = []
		self.just_died = None
		self.players_wounded = []
		self.monsters_slain = []
		self.monsters_wounded = []
		self.rounds = 0
		self.total_dam_to_players = 0
		self.total_dam_to_monsters = 0
		self.players_perfect_blow = []
		self.gold_won = 0
		self.treasure_won = []
		self.combat_status = self.COMBAT_STATUS_NONE
		
class CombatAction(object):
	def __init__(self, name, description):
		self.name = name
		self.description = description
		
	def is_combat_action(self):
		return True
		
	def is_weapon(self):
		return False
		
	def is_spell(self):
		return False	
		
def all_dead(group):
	for p in group:
		if p.is_alive():
			return False
	return True
	
def add_unique(actions, item):
	for a in actions:
		if a.name == item.name:
			return
	actions.append(item)
	
def choose_action_and_target(attacker, others):
	actions = []

	if attacker.active_weapon is not None and attacker.active_weapon.is_weapon() and attacker.has_skill(attacker.active_weapon.cat):
		add_unique(actions, attacker.active_weapon)
		
	mana_adj = 0
	#casting spells while in armor happens at a deficit
	if attacker.is_wearing_non_magic_armor():
		mana_adj = 1

	for item in attacker.inventory:
		if item.is_spell() and (item.mana + mana_adj) <= attacker.cur_mana and attacker.has_skill(item.cat):
			add_unique(actions, item)
	
	if attacker.has_potions():
		actions.append(CombatAction('drink', 'drink potion.'))
	if attacker.has_scrolls():
		actions.append(CombatAction('read', 'read scroll.'))
	if attacker.has_wands():
		actions.append(CombatAction('wand', 'use wand.'))
	actions.append(CombatAction('draw', 'draw a new weapon to use.'))
	actions.append(CombatAction('block', 'attempt to withdaw, rest, and avoid damage.'))
	actions.append(CombatAction('run', 'flee to the nearest exit!'))
	
	if attacker.can_hide():
		if attacker.is_hidden():
			actions.append(CombatAction('stay hidden', 'recover hp and wait for right moment for suprise attack.'))
		else:
			actions.append(CombatAction('hide', 'use your stealth skill to hide in shadows.'))
	
	print("\n\nActions")
	t = PrettyTable(['sel', 'action', 'max damage', 'mana', 'description'])
	i = 1
	for a in actions:
		if a.is_spell():
			t.add_row([i, a.name, a.damage, a.mana + mana_adj, a.description])
		elif a.is_weapon():
			t.add_row([i, a.name, a.damage, ' ', a.description])
		elif a.is_combat_action():
			t.add_row([i, a.name, ' ', ' ', a.description])
		i = i + 1
		
	print(t.get_string(hrules=HEADER))
	print()
	print("Targets")
	t = PrettyTable(['sel', 'target', 'hp', 'ac', 'disabled'])
	i = 1
	for m in others:
		if m.disabled:
			disabled = 'Yes'
		else:
			disabled = 'No'
		t.add_row([i, m.name, m.cur_hp, m.ac, disabled])
		i = i + 1
	print(t.get_string(hrules=HEADER))
	print()
	show_player_status(attacker)
	
	#get input
	valid = False
	target = None
	while not valid:
		print()
		sel = get_input( attacker.name + " - Enter number of sel action (and optional sel target) -> ")
		iAction = 0
		iTarget = 0
		try:
			if(sel.find(' ') != -1):
				args = sel.split(' ')
				if len(args) == 2:
					iAction = int(args[0])
					iTarget = int(args[1])
			else:
				iAction = int(sel)
		except:
			pass
		if iAction > 0 and iAction <= len(actions):
			if iTarget != 0:
				if iTarget > 0 and iTarget <= len(others):
					target = others[iTarget - 1]

			while target is None or not target.is_alive():
				if iTarget < 0 or iTarget >= len(others):
					iTarget = 0
				target = others[iTarget]
				iTarget += 1
				 
			valid = True
		
	return [actions[iAction - 1], target ]
			

def random_action_target(monster, players, player_actions):
	if len(players) == 0 or all_dead(players):
		return [None, None, None]
	iAction = random.randint(0, len(monster.attacks) - 1)
	iPlayer = random.randint(0, len(players) - 1)
	while not players[iPlayer].is_alive():
		iPlayer = random.randint(0, len(players) - 1)	
	return [ monster.attacks[iAction], players[iPlayer], player_actions[iPlayer] ]
	
def random_target(monster, attack, players, player_actions):
	if len(players) == 0 or all_dead(players):
		return [None, None, None]
	iPlayer = random.randint(0, len(players) - 1)
	while not players[iPlayer].is_alive():
		iPlayer = random.randint(0, len(players) - 1)	
	return [ attack, players[iPlayer], player_actions[iPlayer] ]
	
def show_player_status(p):
	if p.is_trapped():
		print(p.get_trapped_desc())
	elif p.is_disabled():
		print(p.name, 'hp:', p.cur_hp, ' is disabled!')
	else:
		print(p.name, 'hp:', p.cur_hp, 'ac:', p.get_ac(), 'mana:', p.cur_mana)
		
def party_comment(comment, party):
	for p in party:
		if p.is_alive():
			print(comment % p.name)
			break
	
def show_status(players):
	print('Status:')
	for p in players:
		show_player_status(p)
	print()
			
def award_experience(players, monsters):
	exp_total = 0
	for m in monsters:
		m.on_combat_end()
		if not m.is_alive():
			exp_total += m.xp_award
	total_living_players = 0
	for p in players:
		p.on_combat_end()
		if p.is_alive():
			total_living_players += 1
	if total_living_players == 0:
		return
	reward = exp_total / total_living_players
	for p in players:
		if p.is_alive() and reward > 0:
			p.add_xp( reward )
			
def one_dead(group):
	d = 0
	for m in group:
		if not m.is_alive():
			d = d + 1
	return d == 1
	
def half_dead(group):
	d = 0
	for m in group:
		if not m.is_alive():
			d = d + 1
	return d == int(len(group) / 2)
	
#a list of the player targets. We adjust the frequency of monster focus
#by adding attacking players 3 times, spell or blocking characters once.
def add_player_target(player, action, player_targets, player_actions):
	if player.is_hidden():
		return
	if action.is_weapon():
		player_targets.append(player)
		player_targets.append(player)
		player_actions.append(action)
		player_actions.append(action)
	player_targets.append(player)
	player_actions.append(action)
	
def get_tohit_mod(round):
	#to simulate fatigue and increasing
	#likeliness to give and receive damage,
	#adjust to hit up as rounds go on.
	#Also helps reduce super long slogging battles
	#where everyone misses.
	tohit_mod = round / 2
	#cap it at a ridiculous 10. Though 30 rounds is a SUPER long battle.
	if tohit_mod > 10:
		tohit_mod = 10
	return tohit_mod
	
def fight(players, monsters, room, level, mon_attack_first):
	done = False
	round = 1
	moral_check_on_first_dead = False
	moral_check_on_half_dead = False
	level.combat_stats = CombatStats()
	while not done:
		print('-------------------------------------------------------')
		print('Round', round, '\n')
		
		#make sure the armor class is up to date.
		for p in players:
			p.update_armor_class()
			
		#show all player status
		show_status(players)
		
		#adjust tohit modifiers to account for fatigue
		tohit_mod = get_tohit_mod(round)
		
		#a list of the player targets. We adjust the frequency of monster focus
		#by adding attacking players 3 times, spell or blocking characters once.
		player_targets = []
		player_actions = []
		for player in players:
			if not player.is_alive():
				continue
			if all_dead(monsters):
				continue
			if mon_attack_first:
				add_player_target(player, CombatAction('suprised', ''), player_targets, player_actions)
				continue
			if player.is_disabled() or player.is_trapped():
				add_player_target(player, CombatAction('disabled', ''), player_targets, player_actions)
				continue
			action, target = choose_action_and_target(player, monsters)
			if action is None:
				continue
			if action.is_spell():
				player.cur_mana -= action.mana
				#wearing armor incurs a 1 pt mana expense
				if player.is_wearing_non_magic_armor():
					player.cur_mana -= 1
				if action.targets_environment():
					action.cast_at_environ(player, monsters, players, room, level)
				elif target is None or action.targets_group():
					action.cast(player, monsters, players)
				else:
					action.cast_at_target(player, target)
			elif action.is_weapon():
				if target is None:
					action.attack(player, monsters, players, tohit_mod)
				else:
					action.attack_target(player, target, tohit_mod)
			elif action.is_combat_action():
				if action.name == 'block':
					hp_rec = HP_RECOVERED_FROM_REST * player.level
					if player.cur_hp <= (player.hp / 2) - hp_rec:
						player.cur_hp += hp_rec
						print(player.name, 'regains', hp_rec, 'hp after blocking and resting.')
				elif action.name == 'run':
					num_items = len(player.inventory)
					if num_items > 0:
						iDrop = random.randint(0, num_items - 1)
						item = player.inventory[iDrop]
						if not item.is_weapon() and not item.is_spell() and not item.is_armor():
							print(player.name, 'bolts for the door and drops his', item.name, 'in haste!')
							player.remove(item.name)
							room.items.append(item)
					award_experience(players, monsters)
					#all monsters heal when you leave.						
					for m in monsters:
						if m.is_alive():
							m.cur_hp = m.hp
					pause()
					return "run"
				elif action.name == 'hide':
					roll = random.randint(1, 20)
					print(player.name, 'rolls %d.' % roll)
					if roll >= player.get_hide_roll_thresh():
						print(player.name, 'slips into the shadows silently.')
						player.set_hidden(True)
					else:
						print(player.name, 'was not able to hide.')
				elif action.name == 'draw':
					room.activate([player])
				elif action.name == 'drink':
					player.drink_potion()
				elif action.name == 'read':
					player.read_scroll(monsters, players, room, level)
				elif action.name == 'wand':
					player.use_wand(monsters, players, room, level)
			pause()
				
			if player.is_hidden():
				if action.is_spell() or action.is_weapon():
					player.set_hidden(False)
				elif action.name != 'run':
					hp_rec = HP_RECOVERED_FROM_REST * player.level
					if player.cur_hp <= (player.hp / 2) - hp_rec:
						player.cur_hp += hp_rec
						print(player.name, 'regains', hp_rec, 'hp while hiding.')
			add_player_target(player, action, player_targets, player_actions)
					
		#check for morale of monsters
		if not moral_check_on_first_dead and one_dead(monsters) and len(monsters) > 1:
			moral_check_on_first_dead = True
			if random.randint(1, 10) < 4:
				print('The rest of the creatures flee in terror!')
				award_experience(players, monsters)
				return 'won'
		if not moral_check_on_half_dead and half_dead(monsters) and len(monsters) > 3:
			moral_check_on_half_dead = True
			if random.randint(1, 10) < 5:
				print('The rest of the creatures flee in terror!')
				award_experience(players, monsters)
				return 'won'
		
		#only use once. Surprise attack
		if mon_attack_first:
			if random.randint(1, 2) < 2:
				print("It's a surprise attack!")
				tohit_mod += 2
			else:
				party_comment('%s yells, "Look out!"', players) 
			mon_attack_first = False
		
		for monster in monsters:
			action = monster.take_combat_turn(player_targets, player_actions, room, level, tohit_mod)
			if action and action.name == 'run':
				monsters.remove(monster)
			
		if all_dead(monsters):
			print("You defeated all the enemies!!\n")
			sitch = [WON]
			print_comment(sitch, players, room, level)
			award_experience(players, monsters)
			return 'won'
			
		if all_dead(players):
			print('And everything fades to black. Better to have run.. oh well!!')
			return 'died'
			
		for monster in monsters:
			if monster.is_alive():
				monster.on_combat_round_ended()
		for player in players:
			if player.is_alive():
				player.on_combat_round_ended()
		print()
		round = round + 1
		
