import random
import copy

from adventure import *
from stuff import *
from shop import *
from util import *
import combat

levelBanner = '''
___________.__                                  
\__    ___/|  |__   ____                        
  |    |   |  |  \_/ __ \                       
  |    |   |   Y  \  ___/                       
  |____|   |___|  /\___  >                      
                \/     \/                       
__________                                  .___
\______   \_____     ____   ____   ____   __| _/
 |       _/\__  \   / ___\ / ___\_/ __ \ / __ | 
 |    |   \ / __ \_/ /_/  > /_/  >  ___// /_/ | 
 |____|_  /(____  /\___  /\___  / \___  >____ | 
        \/      \//_____//_____/      \/     \/ 
 ____  __.                                      
|    |/ _|____   ____ ______                    
|      <_/ __ \_/ __ \\____ \                   
|    |  \  ___/\  ___/|  |_> >                  
|____|__ \___  >\___  >   __/                   
        \/   \/     \/|__|         
'''

home = Room('Home',
'''You sit at the rickety table on the dirt floor of your one room home. 
"Go make some money!", yells your old grandpa from his bed in the rafters. 
"Uhhhh, ok. Whut shud I do?", you mutter. 
"Go to the Ragged Keep!" shrieks the old man. "Clear the dungeon and win arm-loads of gold. Get your skinny butt down there and get some!!!"''',
 '''A rickety table squats on the dirt floor of your one room home.
Snoring floats down from a bed in the rafters.
''',
	'that somehow your dirty, shack of a home looks even worse on the outside.',
	 
	[ITEM('water')])

path_to_keep = Room('Aclovar Main Road', "Sunlight hurts your eyes as you step out onto this loud and noisy road. Countless carts wobble by, pulled by scraggly horses. Men trundle by with packages and sour looks, trying to avoid stepping in horse poo.",
	'Carts, horses, and men trundle by on the muddy dirt road to the keep.', 
	'a heavily rutted, crowded dirt road.')
	
class PigFarmQueryResponse(QueryResponse):
	def __init__(self):
		self.pig_gold_avail = 3
		
	def query(self):
		if self.pig_gold_avail < 2:
			return '''Sherry grins, "Wow, you again! Couldn't get enough of that pig poop?" (y, n) -> ''' 
		if self.pig_gold_avail < 3:
			return '''Sherry grins, "Welcome back! Did you come to work some more?" (y, n) -> ''' 
		return '''Sherry smiles as she sees you walk up. "Looking for work?" She tosses you a shovel. "Shovel pig poop for a day and I'll give you a gold piece for your effort. (y, n) -> '''

	def response(self, reply, party):
		if reply == 'y':
			tg = 0
			for p in party:
				tg += p.gp
			if tg < 10 and self.pig_gold_avail == 0: #have mercy on poor groups..
				self.pig_gold_avail = 1
			if self.pig_gold_avail > 0:
				print('The smell was far worse than you imagined. And as the sun sets, you limp back to Sherry and she deposits a single gold piece into your hand with a smile.')
				for p in party:
					p.gp += 1
				if tg < 10:
					print('With a wink and look to see if no one is checking, she gives you some more. "I know you need it, honey!"')
					for p in party:
						p.gp += 3
				self.pig_gold_avail -= 1
			else:
				print('''"Sorry honey. I just realised I'm out of money. At least I figured that out before you started to shovel all day. Ha Ha."''')
				roll = random.randint(1, 20)
				if roll < 3:
					self.pig_gold_avail = 3
		else:
			print('''Sherry huffs, "Suit yourself. Think your special, huh? I'll be seeing you again, I bet."''')
		return False
	
pig_farm = Room("Sherry's Pig Farm",
	"A squat little shack sits next to two large fenced mud pits full of pigs. There must be at least 50 of them.\nThey are milling about but mostly eating from a long trough. A group of people are at one end with shovels and a horrible smell comes from them.",
	"Pigs mill about in two large fenced areas.", 'a dirt trail leads down to a farm.', [], [], [PigFarmQueryResponse()])

class GateKeeper(EvilNPC):
	called_guards = False
	was_attacked = False
	
	def take_combat_turn(self, players, player_actions, room, level, tohit_mod):
		self.was_attacked = True
		if not self.called_guards and self.is_alive() and not self.is_disabled():
			self.called_guards = True
			print('''"I don't have time for this!" growls the gatekeeper.''')
			print('He takes out a silver whistle and blows it loudly. 10 guards come rushing from the gate!')
			for i in range(0, 10):
				g = EvilNPC('Garison Guard', 'A gruff armored lout.', 50, [ MonsterAttack('speared', 12) ], 100, ac=0 ) 
				room.monsters.append(g)
			pause()
		else:
			super(GateKeeper, self).take_combat_turn(players, player_actions, room, level, tohit_mod)

gatekeeper = GateKeeper('Gatekeeper', 'A stout little man with dark beard and bushy eybrows sits at the table.', 50, [ MonsterAttack('hacked', 10) ], 100, 1 )

keep_gate = Door('a large rusty gate set in stone.')

red_ticket = Item('red ticket', 'a bit of reddish paper. Admit one scribbled in pencil.')

class TicketQueryResponse(QueryResponse):
	def __init__(self, ticket, gatekeeper, gate):
		self.ticket_price = 3
		self.ticket = ticket
		self.gatekeeper = gatekeeper
		self.gate = gate
		
	def do_trigger_on_monsters_dead(self, room, party, level):
		return self.gatekeeper.cur_hp == 0
		
	def query(self):
		if self.gatekeeper.cur_hp == 0:
			return '''
The Gatekeeper lies face down in the mud. Red tickets float everywhere.
Hmmmmm. I wonder who will give us the reward for cleaning the dungeon now? ...uhh
Grab a ticket? 
(y/n) -> '''
		if self.gatekeeper.was_attacked:
			self.ticket_price = 10
			return '''The Gatekeeper scowls at you darkly. "Hey, I remember you!! You are that scurvy rat that attacked me!! It'll be 10 gold for your ticket now!!!"\nGive the gatekeeper 10 gold? (y, n) -> '''
		return '''
When your turn comes, the fat, bearded man snorts, "Name?" and then scribbles it on a dirty ledger. He mouths the letters silently as he writes. His pudgy hand opens as he looks up at you. "3 gold to enter the Keep. Kill all the critters and claim your reward, if ye make it. Heh, heh."
	
Give the gatekeeper 3 gold? (y, n) -> '''

	def response(self, reply, party):
		ret_val = False
		if reply == 'y':			
			if self.gatekeeper.cur_hp == 0:
				p = party[0]
				print(p.name, 'takes a red ticket from the mud and wipes it off.')
				p.add(self.ticket)
				self.gate.unlock()
				return True
			for p in party:
				if p.gp >= self.ticket_price:
					p.gp -= self.ticket_price
					print(p.name, 'gives %d gold to the gatekeeper. He hands you a red ticket.' % self.ticket_price)
					p.add(self.ticket)
					self.gate.unlock()
					ret_val = True
			if ret_val is False:
				print('''"None of ye has the gold for the ticket? I see pig poop in yur future. Better be off to Sherry's Pig Farm then, heh heh. NEXT!!"''')
			else:
				print('''The gatekeeper points a dirty thumb over his shoulder and shouts, "NEXT!!!" ''')
		else:
			print('''"Eh? Stood in line that long but don't want to pay? Must be daft, you are. NEXT!!"''')
		return ret_val
	
sell_tickets = TicketQueryResponse(red_ticket, gatekeeper, keep_gate)
	
gate = Room('The Ragged Keep Gate', 
	'''
A long line of young men wait in front of a dirty table. Above the table hangs a scribbled sign "Git yur ticket here." 

One lad says to another, "I'm not so sure about this. I've heard bad things about the dungeon here. No one's come out alive!"

Another hisses, "Look! It's Baron Von Heiber.. sheiber... beeber.. whatever. He's as cold as they come. Lock you up as much as look at you. He's the one what owns this keep."

A large man in flowery red silk shirt with a large red hat rides towards the keep on a white horse. A train of armor clad knights and squires follow in attendance. He looks down on the line of adventures with a sneer and wry smile. "What a fine looking lot you are. Fame and fortune for you all!", and he tips is hat and continues inside.
	''', 
	'A long line of young men wait in front of a dirty table.',
	"a ragged looking keep which seems to fit it's name.", [], [gatekeeper], [sell_tickets])

set_new_shop_inventory(everything)

bazar = ShopRoom('Ye old Bazar', None,
	'Large colored cloth hangs overhead to block the scortching sun. In the relative shade are countless tables filled with crazy items from all over the world.' , 
	'plumes of smoke rise from the busy and noisy market.', 
	everything)
			
temple = Room('Temple of Light', None, "This impressive stone building has spires that reach for the sky, windows stained in iridescent colors, and shining golden statues in it's cool interior.", 'a large, stone temple.', [], [], [TempleQueryResponse()])
	
class LargeKid(EvilNPC):

	run_action = combat.CombatAction('run', 'flee to the nearest exit!')
	
	def take_combat_turn(self, players, player_actions, room, level, tohit_mod):
		if self.is_alive() and not self.is_disabled():
			print('''"You won't live to regret this!" growls the large kid.''')
			print('He turns heel and dashes into the keep. An iron gate slams shut behind him.')
			pause()
			return self.run_action
		else:
			return super(LargeKid, self).take_combat_turn(players, player_actions, room, level, tohit_mod)
	
large_kid = LargeKid('Large boy', 'The large kid in armor eyes you warrily.', 10, [ MonsterAttack('hacked', 8) ], 15, 1 )

courtyard = Room('Ragged Keep Courtyard',
"Young men are milling about, sharpening their swords and practicing their magic. A large kid is showing off his two handed sword, smacking others on the behind and laughing. He has a funny helm with one horn. Everyone is avoiding looking at the entrance to the dungeon to the east.",
"A crowd of young men killing time in the courtyard.", 'the keep courtyard.', [  ], [ large_kid ] )

dungeon_entrance = Room('Ragged Keep Dungeon Entrance',
'A large wooden arch holds up the entrance to this dark tunnel. Inside a torch burns on the wall casting scary shadows over the rock walls of the stone blocks. Steps lead down further to a small room. Here, a wooden sign is posted on the wall: "Good Luck! Yours, Baron Von Heibeiverstein". The letters are nearly scratched off from sword marks.',
'A small room with a dumb sign. The distant daylight can be seen at the top of the stairs.', 'a small entry room to the dungeon.')

old_bones = Item('old bones', 'a pile of old bones, probably from a cat', 'hidden in the rags.', GP(1))

monster_party = Room('Monster Party',
"Drums and piles of rags lay around this large stone room. In the center is a large table with what might be called a cake. But eeewww, it does not look yummy.",
"A large stone room. A table with questionable cake sits in the center.",
"a long dark tunnel.", [ old_bones ], [Mon('Orc', 'The Orcs are beating drums and dancing in a circle. They are very bad dancers. And even worse singers.'), Mon('Orc'), Mon('Orc'), Mon('Orc')])

golden_skull = Item('golden skull', 'a wicked looking gold skull', 'hidden among the spider webs. It looks quite valuable.', GP(20))

spiders_nest = Room('Spiders Nest',
"Over-turned tables and smashed chairs lay about the stone room covered in cob-webs. You have a funny feeling that many eyes are watching you.",
"A messy room covered in cobwebs.",
"a small door covered in spider webs.", [ golden_skull ], [Mon('Giant Crab Spider', 'The spiders slowly crawl to the edge of their web and peer at you.\nIt could be your imagination but you think you hear them giggling.'), Mon('Giant Crab Spider'), Mon('Giant Crab Spider')] )

threeds = Item('3ds', 'a Nintendo 3DS game system', 'plugged into the wall. Probably some kid forgot about it.', GP(10))

snakes_den = Room('Snakes Den',
"Many small snakes slither on the floor of this dark, wet cave. It's kind of scary actually.",
"Somewhat scary, wet cave full of snakes.",
"a wet, dark cave.", [threeds], [ Mon('Giant Rock Python', 'A large snake with green and brown scales is coiled around a large pillar in the middle of the room. He tests the air with his tounge and watches you carefully.')])

bucket = Item('bucket of tickets', 'a yellow metal bucket stuffed full of red tickets', 'just at the edge of the stage. Hmm. These look just like the tickets they sold you to get in here.')

skel_key = Item('skelton key', 'a skeleton key, made of white bone and shapped like a leg.')

skel_door = Door('a wooden door with rusty iron straps holding it together.', skel_key)

skeletons_ball = Room('Skeletons Ball',
"A huge disco ball hangs in the center of this large ball room. Lasers lights shoot around the room as some strange music seems to be playing from the walls.",
"An odd dance floor.",
"flashing lights and hear some strange music drifting down the hall.",
[ bucket, skel_key ], [ Mon('Skeleton', 'Numerous skeletons in rags sway left and right to the music. Their heads nod rythmically to the beat.'), Mon('Skeleton'), Mon('Skeleton'), Mon('Skeleton'), Mon('Skeleton'), Mon('Skeleton') ] )

#A randomly generated maze. It's generated once on first entry.
#It's randomly populated with monsters in every room. Not very interesting,
#but great for level crawl.
class MazeEntrance(Room):
	def on_enter(self, party, level, entered_from_room=None):
		if(entered_from_room.name != 'MonMaze'):
			#rebuild the maze on each entry.
			#first clean out the old rooms
			new_connections = dict()
			for direction in self.connect_rooms:
				room, door = self.connect_rooms[direction]
				if room.name != 'MonMaze':
					new_connections[direction] = [room, door]
			self.connect_rooms = new_connections
			party_hp = 0
			for p in party:
				party_hp += p.hp
			limit = 20
			self.iRoom = 0				
			while limit > 1:
				#print 'generating maze...'
				limit = self.generate_maze(self, limit, party_hp)
		super(MazeEntrance, self).on_enter(party, level, entered_from_room)

	def generate_maze(self, room, limit, party_hp, exclude_dir=None):
		if limit <= 0:
			return 0
		d = ['North', 'South', 'East', 'West']
		for dir in d:
			r = None
			if dir == exclude_dir:
				continue
			try:
				r, door = room.connect_rooms[dir]
				if isinstance(r, MazeEntrance):
					continue
				#print 'traverse existing room'
				limit = self.generate_maze(r, limit, party_hp, self.get_opposite(dir))
				if limit <= 0:
					return 0
			except:
				if r is not None:
					continue
				roll = random.randint(1, 100)
				if roll < 33:
					monsters = []
					which = random.randint(0, len(all_monsters) - 1)
					m = all_monsters[which]
					num_mon = random.randint(1, m.no_appearing)
					total_hp = 0
					for i in range(0, num_mon):
						mon = Mon(m.name)
						if i == 0:
							if num_mon == 1:
								mon.description = 'You see a %s. It looks like %s' % (m.name, m.description)
							else:
								mon.description = 'They looks like %s' % (m.description)
						monsters.append(mon)
						total_hp += monsters[i].hp
						#limit to no more than 2 x player total hp
						if total_hp > party_hp * 2:
							break
					nr = Room('MonMaze', 'Yet another bare room with red circle in the middle.', 'Room with red circle', 'another room.', [], monsters)
					limit = limit - 1
					nr.iRoom = limit
					#indicate that we are calc hardness scale as we go
					nr.dif_scale = 1.0
					#print 'adding maze room', limit, dir, room.name, room.iRoom, 'to', nr.iRoom					
					room.connect(dir, nr)
					limit = self.generate_maze(nr, limit, party_hp)
					if limit <= 0:
						return 0
		return limit

monster_maze_entrance = MazeEntrance('Monster Maze Entrance',
'A bronze plaque on the wall reads "Here in lies the most confusing set of little rooms filled with all sort of nastiness."', 'A bare room with threatening sign.', 'the entrance to the magic monster maze!')


Juno = GoodNPC('Juno')
Juno.age = 8
Juno.sp = 0
Juno.skills.append(new_skill(SKILL_CAT_SHORT_EDGE))
Juno.skills.append(new_skill(SKILL_CAT_ARMOR))
Juno.hp = 5
Juno.cur_hp = 5
Juno.description = 'The young boy in rags with a shock of red hair and large eyes looks at you.'

class SmallBoyResponse(QueryResponse):
	room = None
	
	def query(self):
		return 'The young boy grabs your hand. "Can I please join your party and help me find my brother?" (y, n) -> '
		
	def response(self, reply, party):
		if reply == 'y':
			print('''\n"Super!! My name is Juno. I won't be much trouble. My brother Jared will be so happy when he sees us!''')
			print('''\n"Oh, can someone give me a dagger or short sword? I can help in a battle."''')
			print('Juno joins your party.')
			Juno.update_attribute_mods()
			party.append(Juno)
		else:
			print('''\n"Awww. Ok. I understand. Thanks for letting me free anyway." And with that he scampers away down the hall.''')
		if self.room is not None:
			self.room.monsters = []
		return True

sbqr = SmallBoyResponse()

kitchen_key = Item('large iron key', 'a large iron key', 'on a hook hidden by the door.')

kitchen_door = Door('A large iron door with small keyhole.', kitchen_key)

small_cell = Room('A Small Cell',
'''
This is a dark and dingy room with a single flickering torch on one wall. 
There is a small mound of straw that might be someone's bed. It seems as if someone has been sleeping here for a long time. 
In fact, you see two large eyes blinking underneath a shock of red hair, and then a large smile from a small boy!

"Oh my!!", he shouts. "I've been locked in here for days! Do you have any food or water? Oh, thank you!!"
He starts munching the food you gave him and slurping your water greedily.

"Hey, slow down", you say. "Why are you here?"

"Oh, don't you know? The Baron captures all the people that enter here. 
I was just coming to try to save my brother. He came down a long time ago.
I was looking and looking until these stupid skeletons grabbed me and locked me up.
Oh their music is terrible!" 
''',
'A small dark cell. A small bed of straw.', 'a small cell.', [kitchen_key] , [ Juno ], [ sbqr ] )

sbqr.room = small_cell

stairs_down = Room('Wet Stone Stairway', 'A set of stairs are carved into the side of this cave. They are dipping wet, mossy, and slippery. They lead far down into the darkness.', 'A wet stone stairway.', 'a wet stone stairway.')

magic_sword = MagicWeapon('Golden Short Sword + 1', 'a magic golden blade with silver wrapped hilt. nicely balanced and razor sharp.', 8, 'slashes', GP(100), SKILL_CAT_SHORT_EDGE, None, 1, 1 )

wine_cellar = Room('Wine Cellar', "This large cold room is stacked high with large wooden barrels. They look quite old and have cobwebs on them. But they appear to be full of wine. There's a small table with a few wooden cups and two chairs. It's oddly silent down here. You can hear water dipping from the ceiling.", 'Large wooden barrels are stacked here.', 'a room full of barrels.', [magic_sword], [ Mon('Giant Tarantula', 'Several eyes shine from the darkness behind the barrels. Slowly you see some large shapes emerge without a sound, their fangs shining in the torch light.'), Mon('Giant Tarantula') ] )

note_from_Juno = Item('Note', 'a note written hastilly on jar', '"Jared. If you find this, they are taking me to the ball room, I think. I have to go, I think they see " and then the note ends.')

food_store = Room('Food Storage', "Boxes and boxes of fruits, bread, cheese, dried meats, and some things you don't recognize line the shelves of this store room. It's nice and cool in here. And very dry.", "A cool, dry food store room.", "a food store room.", [ ITEM('bread'), ITEM('bread'), ITEM('bread'), ITEM('water'), ITEM('water'), ITEM('water'), note_from_Juno ])

kitchen_ogre = Mon('Ogre', "A tall, sinister human like creature towers over a crowd of smaller orcs, yelling and spanking them with his spoon. His large, dirty, white cooks hat looks crazy wobbling on his hairy head.")

kitchen_monsters = [ kitchen_ogre, Mon('Orc'), Mon('Orc'), Mon('Orc'), Mon('Orc'), Mon('Orc') ]

class KitchenCaptivesQueryResponse(QueryResponse):
	def do_query_on_enter(self):
		return False
	
	def do_query_on_monsters_dead(self):
		return True
		
	def query(self):
		return '\nThe people in chains start cheering!! "Thank you so much for saving us. Will you unlock our chains? (y, n) -> " '
		
	def response(self, reply, party):
		if reply == 'y':
			print(''' They all start thanking you over and over. "There's so many more!" They all start shouting at once. "The Baron has many of us working in the mines. We are the lucky ones."		''')
			if in_party(party, "Juno"):
				J = get_player(party, "Juno")
				if J.is_alive():
					print('''\nOne small boy cries out, "Juno! Oh you managed to escape! Your brother still lives. He is working in the mines, I think."
Juno smiles big, "Thank you... thank you for telling me."
					''')
				else:
					print('''
					One small boy cries out, "Oh Juno! Are you ok?! I'm sure he would like to know his brother still lives. I think he's in the mines now."
					''')
			else:
				print('''\nOne small boy cries out, "Have you seen Juno? He managed to escape but we haven't seen him for ages! I'm sure he would like to know his brother still lives. I think he's in the mines now. I hope Juno made it out safely!"
				''')
			for p in party:
				p.add_xp(10)
		else:
			print('"Oooooo.. you are so unbelievably mean!!! I hope you grow old... and get warts on your bum!"')
		return True

kitchen = Room('Kitchen', "This large room is filled with multiple large stewing pots. Various cooking utensils and ingredients are stacked on shelves around the edge of the room. Several large skinned animals turn on skewers over the fire.\n\nNumerous people are working around the kitchen. They appear to have chains on their legs.\n", 'A large room full of boiling pots.', 'a large kitchen.' , [ITEM('bread'),ITEM('bread'),ITEM('water')], kitchen_monsters, [KitchenCaptivesQueryResponse()] )

furnace_room = Room('Furnaces', "This rooms is full of three huge copper tanks. Under each a large coal fire is stoking. You can see the pipes and plumbing going up into the ceiling. A small underground stream runs in from an opening in the side of the room. A dirty coal cart sits at one end of the room full of coal. It sits on tracks that run down and out of the room.", "A room with large copper water tanks and plumbing. Cart tracks run out of the room.", "a blazing hot room.")

underground_bridge = Room('Rickety Bridge', "The cart tracks lead into this underground cavern. It opens up into a large space, so inky black you can't see where it ends. A wooden bridge is built here for the tracks that run to the caves on the other side. The bridge is wobbly but seems stable enough to cross.", "A wobbly wooden bridges spans the darkness to the caves.", "a wooden bridge.")

class ShovelingCaptivesQueryResponse(QueryResponse):
	def do_query_on_enter(self):
		return False
	
	def do_query_on_monsters_dead(self):
		return True
		
	def query(self):
		return '''\nThe people in chains cheer weakly, coughing. "You are the one's we heard about! Will you unlock our chains? (y, n) -> " '''
		
	def response(self, reply, party):
		if reply == 'y':
			print('''\n\n They all start thanking you over and over. "We heard the guards talking about someone freeing the kitchen!", they all say at once. "The Baron is hopping mad! We saw him spit with rage when he heard, he did. He was just here inspecting us, not but a short time ago."\n\n		''')
			for p in party:
				p.add_xp(10)
		else:
			print('"ehh.. you are so cruel!!! I hope you turn blind and get stuck in maze!"')
		return True
		
small_diamond = Item("small diamond", "a small white gem gleaming brightly", "in the dirt underneath one of the carts.", GP(50))
		
loading_room = Room('Loading Room', "The cart tracks lead into this long room with a very low ceiling. Piles of coal are stacked at one end. Many people are shovelling it into the carts waiting on the tracks. They are chained to a large rock in the middle of the room.", "Piles of coal sit next to waiting carts.", 'a long room with many carts.', [small_diamond], [Mon('Orc', "Numerous orcs stand guard over the people, shouting and whipping them."), Mon('Orc'), Mon('Orc'), Mon('Orc')], [ShovelingCaptivesQueryResponse()] )

guard_room = Room('Mine Guard Room', "Rows of bunks line the walls. Some Orcs are sleeping here. Others appear to be playing some kind of game with a rat on the table.", "Rows of bunks and tables line the room.", 'a guard room.', [], [Mon('Orc', 'One ugly, little yellow creature turns and blinks. "Hay. Wut r you doin here?"'), Mon('Orc'), Mon('Orc'), Mon('Orc')])

mining_tunnel = Room("Mine Tunnel", None, "Cart tracks run down this low tunnel of rock. A small path runs along the side of it.", "a dark tunnel.")

def TUN():
	return copy.deepcopy(mining_tunnel)
	
tun1 = TUN()
tun2 = TUN()
tun3 = TUN()
tun4 = TUN()
tun5 = TUN()

depot_ogre = Mon('Ogre', 'A tall, sinister human like creatures tower over a crowd of smaller orcs and men, yelling and whipping them.\nThe crowd of people cry out, "They are here to save us!!", and the large Ogre turns with a roar. \n"Get them!!" he snarls.')

depot_monsters = [ depot_ogre, Mon('Orc'), Mon('Orc'), Mon('Orc'), Mon('Orc'), Mon('Orc'), Mon('Orc') ]

class DepotCaptivesQueryResponse(QueryResponse):
	def do_query_on_enter(self):
		return False
	
	def do_query_on_monsters_dead(self):
		return True
		
	def query(self):
		return '''\nThe people in chains cheer wildly, whooping with joy. "You are the one's we heard about! Will you unlock our chains? (y, n) -> " '''
		
	def response(self, reply, party):
		if reply == 'y':
			print('''\n\n They all cheer and thank you over and over. "We heard the guards talking!", they all say at once. "But we can hardly believe you came."\n''')
			for p in party:
				p.add_xp(100)
			print()
			if in_party(party, "Juno"):
				p = get_player(party, "Juno")
				party.remove(p)
				if p.is_alive():
					print('''One large dirty boy cries out, "Juno!!!"
Juno races over the rubble and jumps into his arms "Jared!!! I never thought I'd see you again!!", he sobbed with happiness. Everyone cheers once again for the reunion.\n''')
				else:
					print('''One large dirty boy cries out, "Juno!!!"
Jared races over the rubble and holds a limp Juno in his arms "Juno!!! I never thought I'd see you again!!", he sobbed with happiness and sorrow. "We must get him to a priest!" Everyone agrees and they hoist him upon their shoulders.\n''')
			print(" The large group of people take up the swords from the fallen orcs. And together the small army marches out of the mines, hand in hand.")
			print()
			print("The Baron was seen fleeing from The Ragged Keep with bags of diamonds. No one knows where he went.")
			print('''
			
___________.__             ___________           .___
\__    ___/|  |__   ____   \_   _____/ ____    __| _/
  |    |   |  |  \_/ __ \   |    __)_ /    \  / __ | 
  |    |   |   Y  \  ___/   |        \   |  \/ /_/ | 
  |____|   |___|  /\___  > /_______  /___|  /\____ | 
                \/     \/          \/     \/      \/ 


We hope you enjoyed this text based adventure! Have fun modifying it, or make your own! Check out the README.txt for ways to have fun.
				''')
		else:
			print('''"You won't help us?! Ehh.. you are worse than the Baron!!! A plague on you and your kin for all generations!!!" The crowd starts booing and spitting at you.''')
		return True
		
large_depot = Room("Mine Depot", "This cavernous room is a cacophony of shouting, clanging, and smashing. A long belt carries coal into a massive pounding hammer. This monstrous slab of metal lifts and pounds the coals to bits. Hundreds of people of all ages toil under the lash, chained together in groups, shovelling and carrying coal. Orcs scurry about, watching closely. And over them all, a large Ogre roams with a wicked whip and horned club.\n\n On a balcony overlooking this large room sits the Baron, observing quietly. Next to him stands a boy in armor, with a one horned helm.\n", "A cavernous room filled with coal smashing equipment.", "a cavernous, loud room.", [small_diamond, small_diamond], depot_monsters, [DepotCaptivesQueryResponse()])

#if we have rooms that need to be updated, because of fixes.
class TRG_RoomPostLoadFixer(RoomPostLoadFixer):

	def make_post_load_fixes(self, current_room, loaded_room):
		try:
			#this will convert old saves to the new structure
			loaded_room.room_actions = loaded_room.query_response
		except:
			pass
		if loaded_room.name == large_depot.name:
			if len(loaded_room.monsters) == 8:
				#this fixes the ogre that appeared twice, but was the same instance.
				loaded_room.monsters = depot_monsters
				loaded_room.initial_description = current_room.initial_description

#assign this callback in order to make fixes to games that were saved in a 'bad' state.
set_post_load_room_fixer(TRG_RoomPostLoadFixer())
	
'''
The Level layout. Connect all the rooms together.
'''

level1 = Level ("The Ragged Keep", levelBanner)

#in-town
home.connect("North", path_to_keep)
path_to_keep.connect("North", gate)
path_to_keep.connect("West", bazar)
path_to_keep.connect("East", pig_farm)
gate.connect("North", courtyard, keep_gate)
courtyard.connect("East", dungeon_entrance)
courtyard.connect("West", temple)

#upper level
dungeon_entrance.connect("North", monster_party)
dungeon_entrance.connect("South", spiders_nest)
dungeon_entrance.connect("East", snakes_den)
snakes_den.connect("East", monster_maze_entrance)
monster_party.connect("North", skeletons_ball)
skeletons_ball.connect("North", small_cell, skel_door)

#lower level
spiders_nest.connect("South", stairs_down)
stairs_down.connect("South", wine_cellar)
wine_cellar.connect("West", food_store)
food_store.connect("West", kitchen, kitchen_door)
kitchen.connect("North", furnace_room)
furnace_room.connect("North", underground_bridge)
underground_bridge.connect("North", loading_room)
loading_room.connect("West", guard_room)
loading_room.connect("North", tun1 )
loading_room.connect("East", tun2 )
tun2.connect("North", tun3 )
tun3.connect("East", tun4 )
tun4.connect("North", tun5 )
tun5.connect("East", large_depot )

run_adventure(level1, home)
