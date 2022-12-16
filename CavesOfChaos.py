import random, copy

from adventure import *
from stuff import *
from shop import *
from util import *
from level import LevelLogic


level_banner = '''
___________.__                                       
\__    ___/|  |__   ____                             
  |    |   |  |  \_/ __ \                            
  |    |   |   Y  \  ___/                            
  |____|   |___|  /\___  >                           
                \/     \/                            
_________                                            
\_   ___ \_____ ___  __ ____   ______                
/    \  \/\__  \\  \/ // __ \ /  ___/                
\     \____/ __ \\   /\  ___/ \___ \                 
 \______  (____  /\_/  \___  >____  >                
        \/     \/          \/     \/                 
        _____  _________ .__                         
  _____/ ____\ \_   ___ \|  |__ _____    ____  ______
 /  _ \   __\  /    \  \/|  |  \\__  \  /  _ \/  ___/
(  <_> )  |    \     \___|   Y  \/ __ \(  <_> )___ \ 
 \____/|__|     \______  /___|  (____  /\____/____  >
                       \/     \/     \/           \/   
'''

########################################################
## Mission requirements

#These are the 7 shards that need to be collected to finish the quest.
shard1 = Item('Shard of Erreanstone', 'a gold shard of glimering stone', "hanging from a chain on the chieftain's neck!", GP(0))
shard2 = Item('Shard of Erreanstone', 'a red shard of glimering stone', "set in the armored breast plate of the chieftain.", GP(0))
shard3 = Item('Shard of Erreanstone', 'a white shard of glimering stone', "set in the crown of the chieftain's helm.", GP(0))
shard4 = Item('Shard of Erreanstone', 'a green shard of glimering stone', "in a black velvet pouch on the table by the bed.", GP(0))
shard5 = Item('Shard of Erreanstone', 'a turquois shard of glimering stone', "in a fur lined pouch in the large sack.", GP(0))
shard6 = Item('Shard of Erreanstone', 'a black shard of glimering stone', 'in the hidden false bottom of an iron chest.', GP(0))
shard7 = Item('Shard of Erreanstone', 'a blue shard of glimering stone', 'set in the necklace of the chieftain!', GP(0))

#keeping them in a list makes it easier to check
all_shards = [shard1, shard2, shard3, shard4, shard5, shard6, shard7]

#each update, we check for quest complete
def have_all_shards(party):
	for shard in all_shards:
		found = False
		for p in party:
			if found:
				continue
			for item in p.inventory:
				if item.description is not None and item.description == shard.description:
					found = True
					break
		if not found:
			return False
	return True
	
end_message = '''

Congratulations! You have recovered all 7 Shards of Erreanstone!!

After your long journey home, the townfolk of Aclovar greet you with a ticker tape parade. A huge feast is held in your honor. Some talk of making you mayor. Others just love an excuse to party.
			
___________.__             ___________           .___
\__    ___/|  |__   ____   \_   _____/ ____    __| _/
  |    |   |  |  \_/ __ \   |    __)_ /    \  / __ | 
  |    |   |   Y  \  ___/   |        \   |  \/ /_/ | 
  |____|   |___|  /\___  > /_______  /___|  /\____ | 
                \/     \/          \/     \/      \/ 


We hope you enjoyed this text based adventure! Have fun modifying it, or make your own! Check out the README.txt for ways to have fun.

'''
	
class CavesLevelLogic(LevelLogic):
	def do_update(self, room, party):
		done = have_all_shards(party)
		if done:
			global end_message
			print(end_message)
			if util.CRAWL:
				while True:
					pass
			for p in party:
				p.add_xp(100)
			#take all the shards, before they can be given to anyone.
			for p in party:
				while p.remove('Shard of Erreanstone') is not None:
					pass
		return done


########################################################
## Town of Kendar

class InnSearch(RoomTrigger):

	def __init__(self):
		self.comments = []
		self.comments.append('While your head is peeking under the table, you catch the eye of a scary, ragged, old woman at a table across the room. She gives you a wink and gets up to leave.')

	def do_trigger_on_search(self, room, party, level):
		return True
		
	def on_triggered(self, room, party, level):
		for c in self.comments:
			print(c)
			self.comments.remove(c)
			break
		return len(self.comments) == 0

inn = Room("The Drunken Sow Inn", '''Crowds of travellers huddle around wooden tables and multiple roaring fires, attempting to fight the chill. It's been raining for days and mud cakes the floor and makes it slippery. Your party sits alone, sipping spiced, warm drinks in a dark alcove next to the kitchen door.

It's been weeks since the discovery of the Baron's evil doings in The Ragged Keep. Aclovar towns folk hailed you as heroes and many a drink was had in your honor. Even your old grandfather joined the festivities, if only long enough to find a chicken leg.

The wicked Baron had fled the keep. His nephew, barely better, discovered huge debts owed to the neighboring king of Atlonia. When the kings tax collector came calling, everyone turned to you. The debt was huge and unpayable. The kings court sent word that as payment, they would accept an act of fealty that was tantamount to death. They demanded the recovery of the 7 Shards of Erreanstone, and in so doing, making safe the Caves of Chaos. Legend holds that the Erreanstone was shattered and the shards were scattered through the caves.

Having been unanimously voted into the mission, your party sits here, in the mountain town of Kendar, after 5 days of hard travel through the mountain passes.
''', 'A crowded and noisey inn. Travellers huddle around table and fire, seeking warmth and food.', 'the warm lights of the Drunken Sow Inn.', [], [], [InnSearch()])

class RumorsQueryResponse(QueryResponse):
	def __init__(self):
		self.rumors = []
		self.rumors.append('A merchant, imprisoned in the caves, will reward his rescuers.')
		self.rumors.append('A powerful magic-user will destroy all cave invaders.')
		self.rumors.append('Tribes of different creatures live in different caves.')
		self.rumors.append('An ogre sometimes helps the cave dwelers.')
		self.rumors.append('A magic wand was lost in the caves area.')
		self.rumors.append('All the cave entrances are trapped.')
		self.rumors.append('If you get lost, beware the eater of men!')
		self.rumors.append('Altars are very dangerous.')
		self.rumors.append('A fair maiden is imprisioned within the caves.')
		self.rumors.append('"Bree-yark" is goblin-language for "we surrender"!')
		self.rumors.append('Beware of treachery from within your party.')
		self.rumors.append('The big dog-men live very high in the caves.')
		self.rumors.append('There are hordes of tiny dog men in the lower caves.')
		self.rumors.append('Piles of magic armor are hoarded in the southern caves.')
		self.rumors.append('The bugbears in the caves are afraid of dwarves!')
		self.rumors.append('Lizard-men live in the marshes.')
		self.rumors.append('An elf once disappeared in the forest.')
		self.rumors.append('Beware the mad hermit of the forrest.')
		self.rumors.append('Nobody has every returned from an expedition to the caves.')
		self.rumors.append('There is more than one tribe of orcs within the caves.')
		
		self.delivery = []
		self.delivery.append('She fixes you with her one good eye, shining widely, and whispers, "%s"')
		self.delivery.append('Speaking in low tones, she leans towards you, "%s"')
		self.delivery.append('She covers her mouth so only you can see, "%s"')
		self.delivery.append('After a quick look around, she hisses, "%s"')
		self.delivery.append('"%s" she says with a knowing smile and a nod.')
		self.delivery.append('"%s" She pauses, "And dont let me catch you repeating that!"')
		
	def query(self):
		return 'A ragged woman in bear skin shawl approaches you from the shadows. "I can see you make for the caves. Information I have, but pay you will. One gp for an old woman?" (y, n) -> '
		
	def response(self, reply, party):
		if reply == 'n':
			print('''She shrugs, "Then that's the last you'll see of me." She disappears into the shadows of an alley. You notice she leaves no footprints in the mud.''')
			return True
		while reply == 'y':
			num_rumors = len(self.rumors)
			if num_rumors == 0:
				print('She shrugs, "You are too curious. Be gone with you, before I make something else up." She disappears into the shadows of an alley. You notice she leaves no footprints in the mud.')
				return True
			paid = False
			for p in party:
				if p.gp > 1:
					print(p.name, 'gives her 1gp.')
					p.gp -= 1
					paid = True
					break
			if not paid:
				print('"Ha, you have no coins for me? Then figure it out fer yerself."')
				break
			if num_rumors == 1:
				r = self.rumors[0]
				self.rumors = []
			else:
				iRum = random.randint(0, num_rumors - 1)
				r = self.rumors[iRum]
				self.rumors.remove(r)
			iDel = random.randint(0, len(self.delivery) - 1)
			dl = self.delivery[iDel]
			print((dl % r))
			reply = get_input('"Want to know more? (y, n) -> ')
		return False
			
class RescueWatcher(RoomTrigger):

	def do_trigger_on_enter(self, room, party, level):
		for p in party:
			if p.name == 'Shelila' or p.name == 'Ribald McMillini':
				return True
		return False
		
	def on_triggered(self, room, party, level):
		tr = []
		for p in party:
			if p.name == 'Shelila':
				print('Shelila says, "Home at last! I never thought I would be so happy to see this little town. Let me repay you with these potions." She gives you a big hug and kiss and departs with a wave.\n')
				tr.append(MAG_ITEM("Potion of Healing"))
				tr.append(MAG_ITEM("Potion of Invisibility"))
				party.remove(p)
		for p in party:
			if p.name == 'Ribald McMillini':
				print('Ribald bows, "My Guild thanks you deeply for your service, as do I. Please accept this gold as a small token of our grattitude." He bows once more before leaving.\n')
				tr.append(GP(100))
				party.remove(p)
		if len(tr) > 0:
			divide_loot(party, tr)
		return len(tr) > 0

main_road = Room('Kendar Main Road', 'The rain and countless hooves and feet have made a soupy, muddy mess out of this main road running down through the highlands.\nSmall shops line the road until the distant city gate.', 'A muddy main road of Kendar leading through town.', 'a muddy main road of Kendar.', [], [], [RumorsQueryResponse(), RescueWatcher()])

set_new_shop_inventory(everything)

shop = ShopRoom('Kendar Goods', None,
	'This large, wooden store is deceptively large. The shopkeeper greets you with a yell.' , 
	'a large, wooden, two story building. The "Kendar Goods" sign hangs out front.', 
	everything)

temple = Room('Temple of Light', None, "This impressive stone building has spires that reach for the sky, windows stained in iridescent colors, and shining golden statues in it's cool interior.", 'a large, stone temple.', [], [], [TempleQueryResponse()])

########################################################
## Wilderness of Kendar

forrest = Room('Kendar Forest', 'Exiting the town of Kendar, the trail twists into this dark, wet forest. Moss and lichen grow on twisted root and jagged boulder. Small streams cut through the trail and make the walking slow, and treacherous.', "A dark and treacherous wood.", 'a dark woodland.')

magic_shield = MagicArmor('Magic Shield +1', 'a shining silver shield', GP(80), 2, SKILL_CAT_SHIELD, 'which gleams once the dust and grime are wiped off.\n It was cluctched in the hands of the small elven skeleton, covered in cobwebs.')

spiders_lair = Room('Spiders Lair', 'Large spiders have spun their webs in the trees here. Under a pile of leaves is the skeleton of a hapless elf.', 'A narrow trail through the trees whose branches are filled with webs.\n', 'a narrow trail into the trees.', [magic_shield], [ Mon('Giant Black Widow Spider', "The spiders pause, as if to fool you into thinking they won't pounce on you as you pass."), Mon('Giant Black Widow Spider') ])

mad_hermit = EvilNPC('The Mad Hermit', '''\nA gaunt, disheveled, little man peeks from behind some bushes. His crooked, yellow teeth flash in a smile. "Welcome travellers! I see you met my pet spiders? Perhaps you will like my pet kitty better!!!" He shrieks a wild yell as a mountain lion pounces down from the tree.''', 15, [ MonsterAttack('slashed', 6) ], 30, 1, 4 )

magic_dagger = MagicWeapon('Dagger +1', 'a magic slender blade, fast and light', 4, 'jabs', GP(30), SKILL_CAT_ANY, "still clutched in the mad Hermit's fist.", 1, 1 )

ring_of_protection = MagicArmor('Ring of Protection', 'a magic silver ring', GP(100), 1, SKILL_CAT_ANY, "on the crooked left thumb of the Hermit.")

cup_and_plate = Item('Wooden Cup and plate', 'a hand carved dish set', "inside the hollow of the tree. Bits of rotting fish are still stuck to it.")

mad_hermit_hollow = Room("Hollow of the Mad Hermit", None, "A large, twisted oak dominates this clearing in the wood. The ancient tree is hollow and dead. Dark leaves matt the floor here and the smell of rotting fish permeates the air. A small, stagnant, green pool hides in rushes beyond the tree.", "a large twisted oak in a clearing in the wood.", [ magic_dagger, ring_of_protection, cup_and_plate ], [ mad_hermit, Mon('Mountain Lion')], [ AmbushRoomTrigger() ])

swamp_trail = Room("Swampy Trail", "Descending from the forest seems like a good idea at first, as the way is easier and sloping down. But the ground quickly gets wetter and slightly spongy, turning into a bog. Muddy streams and pools line the sides of the trail.", "A wet and spongy trail through the swamp.", "a trail leading down from the forest.")

gold_ingot = Item('gold ingot', 'a golden slab of metal', "hidden under a nest with eggs.", GP(90))

lizard_men_mounds = Room("Mounds of the Lizard Men", "Several large mounds of earth rise from the swamp. Sticks frame a low entrance to each. A thin, weak smoke rises from the central, largest mound. A large pile of bones lay near the trail end.\n", "Several large earthen mounds in the swamp.", "several large mounds in the swamp.", [gold_ingot], [Mon('Lizard Man', "Several large lizard men cook around a low fire. They have green, scaled human like bodies, but the head of a lizard. They clutch wooden spears with wicked bone tips. They seem to be arguing about their lunch and don't notice you."), Mon('Lizard Man'), Mon('Lizard Man'), Mon('Lizard Man'), Mon('Lizard Man'), Mon('Lizard Man')] )

########################################################
## Caves of Chaos

bones = Item('bones', 'skulls and bits', 'laying in piles on the ravine floor, ewww.')

ravine_initial = ''' The forest you have been passing through has been getting more dense, tangled, and gloomier than before. The thick, twisted tree trunks, unnaturally misshapen limbs, writhing roots, clutching and grasping thorns and briars all seem to warn and ward you off. But you have forced and hacked your way through regardless. 

 Now the strange growth has suddenly ended you have stepped out of the thicket into a ravine like area. The walls rise rather steeply to either side to a height of about 100 ft or so. Clumps of trees grow here and there, both on the floor of the ravine and up the sloping walls of the canyon. The opening you stand in is about 200 ft wide. The ravine runs at least 400 ft north to where the northern end rises in a steep slope. 

 Here and there, at varying heights on all sides of the ravine, you can see the black mouths of cave-like openings in the rock walls. 

 The sunlight is dim, the air dank, there is an oppressive feeling here as if something evil is watching and waiting to pounce upon you. There are bare, dead trees here and there, and upon one a vulture perches and gazes hungrily at you. A flock of ravens rise croaking from the ground, the beat of their wings and their cries magnified by the terrain to sound loud and horrible. Amongst the litter of rubble, boulders, and dead wood scattered about on the ravine floor, you can see bits of gleaming ivory and white. Closer inspection reveals that these are bones and skulls of men, animals, and other things ....

 You know that you have certainly discovered the Caves of Chaos.'''

ravine = Room("Ravine Opening", ravine_initial, "Here and there, at varying heights on all sides of the ravine, you can see the black mouths of cave-like openings in the rock walls.", "a wide ravine opening.", [bones])
	
ravine_floor = Room("Ravine Floor", None, "The middle of the ravine is densely packed with bushes. You only barely squeeze along the creek-bed.", "the ravine floor.")

ravine_end = Room("Ravine End", None, "The ravine ends in a pile of rocks in a small green, pool. A thin waterfall cascades from the high rocks overhead.", "the ravine end.")

trail_a = Room("Lower South East Trail", "A narrow dirt trail indicates some larger creatures have passed along there. And it seems to lead somewhat upward towards the mouth of one of the many cave entrances. You don't recognize the footprints in the mud. But they appear to be from a smaller two legged creature with four clawed toes. Many tracks look fresh.", "A narrow trail leading to the western caves.", 'a narrow trail disappears into underbrush.')

trail_w = Room("Lower South West Trail", None, "This narrow trail winds through the large boulders and mud.", 'a trail leads into some fallen boulders.')

trail_mw = Room("Mid West Trail", None, "This broad trail is cleared of boulders and bears the tramp of many footprints.", 'a broad trail leading to some caves.')

upper_trail_a = Room("Upper South East Trail", None, "A narrow trial forks off and runs upwards, getting rockier and steeper.", 'a narrow steep trail.')

upper_trail_b = Room("Upper East Ridge Trail", None, "A rocky trail leads sideways across a narrow ledge. Footing is treacherous and a fall might be fatal from this height. The wind howls as it whips across the rocky cliff face.", 'a scary rocky ledge.')

upper_trail_c = Room("Upper South West Trail", None, "A trial twists through the boulders and runs upwards.", 'a rocky steep trail.')

n_trail = Room("Lower North Trail", None, "The trail here leads under the waterfall.", 'a wet, rocky trail under the waterfall.')

nw_mid_trail = Room("Mid North West Trail", None, "The trail here is basicly climbing slippery rocks and roots. Occasionally there's some rough stone stairs covered in moss.", "a slippery steep trail.")

nw_upper_trail = Room("Upper North West Trail", None, "The trail here is more rough stone stairs. Less covered in moss as it gets to the top.", "a steep stone stairway.")

ne_mid_trail = Room("Mid North East Trail", None, "The trail here meanders back and forth with steep cutbacks.", "a steep trail of cutbacks.")

########################################################
## Kobold Lair

kobold_entrance_guards = [ Mon('Kobold', "The trees around the cave entrance come alive with shouts as numerous kobolds jump down and attack the party. The kobold is a short, human like, scaled creature with dark rusty brown skin. It has reddish eyes and small white horns."), Mon('Kobold'), Mon('Kobold'), Mon('Kobold'), Mon('Kobold'), Mon('Kobold'), Mon('Kobold'), Mon('Kobold') ]

kobolds_lair = Room("Kobold Lair Entrance", "The cave mouth here opens into cave like tunnel. Piles of small bones and garbage lay near the entrance.", "A cave like tunnel.", "the entrance to a cave.", [], kobold_entrance_guards , [ AmbushRoomTrigger() ])

entrance_trap = Room("Kobold Lair Corridor", "The cave like tunnel continues into the darkness. Kobolds can see in the dark and don't have any torches on the walls.", "The cave like tunnel continues into the darkness. The pitfall here is only noticeable once you know where it is.", "a cave like tunnel.", [], [], [PitfallRoomTrigger()])

kob_guard_room = Room("Kobold Guard Room", "Kobold guards sit at tables, playing some sort of dice game.", "A room with tables.", "a dimly lit room.", [], [Mon('Kobold', "The Kobold guards are not very alert now." ), Mon('Kobold'), Mon('Kobold'), Mon('Kobold'), Mon('Kobold'), Mon('Kobold')])

silver_chain = Item('silver chain', 'a fine chain of silver links, set with semiprecious stones', 'among the trash and debris.', GP(50))

many_rats = []
for i in range(0, 13):
	many_rats.append(Mon('Giant Rat'))

many_rats[0].description = 'Hordes of giant rats crawl over the garbage. Their large, sensitive eyes spot you right away. But they freeze in fear, ready to defend their home.'
	
rat_lair = Room("Rat Lair", "A huge pile of garbage and waste stinks up this cave. The Kobolds throw their scraps here, and rats don't seem to mind.", "A huge pile of garbage.", 'a small dark cave.', [silver_chain], many_rats)

kob_food_key = Item('iron key', 'a large bit of iron', 'hidden in the robes of the chieftain.')
kob_food_door = Door('a wooden door set in the cave wall.', kob_food_key)

kob_food_storage = Room("Kobold Food Storage", None, "This place contains various sorts of dried and salted meat, grain, and vegetables in sacks, boxes, barrels, and piles. there are also bits and pieces of past human victims. The wine in large casks is thin and vinegary.", 'a small cave.', [ ITEM('dried meat'), ITEM('dried meat'), ITEM('dried meat'), ITEM('wine'), ITEM('wine'), ITEM('wine') ] )

kob_elite_guard = Room("Kobold Lair Corridor", None, "A cavelike tunnel.", "a dark cavelike tunnel.", [], [ Mon('Kobold Guard', "Hiding behind the corner, these guards jump out at the party."), Mon('Kobold Guard'), Mon('Kobold Guard')])

kob_chieftain = Monster("Kobold Chieftain", "A huge kobold chieftain wielding a great battle axe stares at down at a group of female kobolds from his throne. They appear to be arguing about something. He wears a necklace set with a large shining gemstone.", 8, [ MonsterAttack('axed', 8) ], 20, 1, 5 )

kob_chieftain_rm = Room("Kobold Chieftain Chambers", None, "A large cave.", "a large cave.", [kob_food_key, shard1], [kob_chieftain, Mon('Female Kobold'), Mon('Female Kobold'), Mon('Female Kobold'), Mon('Female Kobold'), Mon('Female Kobold')])

many_kobolds = []
for i in range(0, 17):
	many_kobolds.append(Mon("Kobold"))
	
many_kobolds[0].description = "Many kobolds are living here, huddled in small groups in the large chamber. They all turn to look at you as you enter, curious about the tall, pale creatures they see."

old_silken_robes = Item("silken robes", "old silken robes with ancient designs", "carefully folded in a cedar box.", GP(150)) 
	
kob_common_chamber = Room("Kobold Common Chambers", None, "The rest of the kobold tribe lives here.", 'a large dark cave.', [old_silken_robes], many_kobolds)

########################################################
## Red Orc Lair

orc_lair_entrance = Room("Red Orc Lair Entrance", None, "The cave entrance opens up into a large cavern with earthen floor. The floor is trampled with many clawed feet. The north wall is decorated with heads and skulls; human, elven, and dwarvish. They sit in niches which checker about 10 feet of the wall. One of the heads appears to be orcish.", 'the entrance to a cave. Red feathers of some large bird frame the top.')

orc_guard_rm = Room("Orc Guard Room", None, "This chamber is full of pallets and shabby clothing hanging on pegs.", 'a small chamber.', [ ITEM('hard tack'), ITEM('water'), ], [ Mon('Orc', 'These orc guards are clearly sleeping on the job. In fact, they almost seem to be snoring too loud. Perhaps they are faking it.'), Mon('Orc'), Mon('Orc'), Mon('Orc')])

orc_banquet_rm = Room("Orc Banquet Area", None, "There is a great fireplace on the south wall. Many tables and benches line this 30 ft by 50 ft chamber. The table at the north end has a large chair at it's head where the orc leader usually holds court. The place is empty of orcs, although there is a small fire of charcoal burning in the fireplace.", 'a large banquet room.')

many_orcs = []
for i in range(0, 12):
	many_orcs.append(Mon('Orc'))
many_orcs[0].description = 'Many orcs are huddled here in small groups.'

orc_common_rm = Room("Orc Common Room", None, "There are sparse furnishing in the room, scattered bedding and piles of clothing and rubbish.", 'a large room.', [], many_orcs)

orc_store_rm_key = Item("Orcish Key", "a strong iron key", "in the pocket of the chieftain.")

orc_storage_door = Door('a stout, iron clad door is set into the wall here.', orc_store_rm_key)

orc_storage_rm = Room("Orc Storage Chamber", None, "Stacks and heaps of supplies pack this small chamber.", 'a storage room.', [ ARMOR('Shield'), ITEM('rope'), ITEM('bread'), ITEM('water'), WEAPON('Two-handed Battle Axe') ] )

orc_magic_shield = MagicArmor('Magic Shield +1', 'a shining silver shield', GP(80), 2, SKILL_CAT_SHIELD, 'on the arm of the orc chieftain.')

orc_chief = Monster("Orc Chieftain", "A huge orc chieftain lounges on a cot, talking with two other orcs on cushions. They *might* be female orcs, it's really hard to tell. He wears a necklace set with a large shining gemstone.", 15, [ MonsterAttack('bashes', 10) ], 30, 1, 3 )

ring_w_gem = Item("Ring w gem", "a golden ring set with a gem", "on the finger of the orc chieftain.", GP(150))

orc_leaders_rm = Room("Orc Leader's Room", None, "The room is carpeted with large tapestries on the walls. The furniture and cot is battered but serviceable. Cushions line the floor in front of the cot.", "a small carpeted room.", [ orc_magic_shield, ring_w_gem, shard2, orc_store_rm_key ], [ orc_chief, Mon('Orc'), Mon('Orc') ] )

########################################################
## White Orc Lair

white_orc_ambush_party = []
for i in range(0, 9):
	white_orc_ambush_party.append(Mon('Orc'))
white_orc_ambush_party[0].description = 'Many orcs lounge here, sharpening swords and eating while chatting.'
	
class FallingNetTrap(RoomTrigger):
	def __init__(self, common_rm):
		self.common_rm = common_rm
		
	def do_trigger_on_enter(self, room, party, level):
		return True
		
	def on_triggered(self, room, party, level):
		num_trapped = 0
		trapped = []
		for p in party:
			if random.randint(1, 6) < 5:
				num_trapped += 1
				if num_trapped == len(party):
					#can't allow everyone to be trapped
					continue
				trapped.append(p)
				any_trapped = True
		if len(trapped) == 0:
			print('Whew! Someone spotted a trip wire and everyone avoided the trap net hanging overhead!')
		else:
			print(trapped[0].name, 'tripped on a secret wire causing a large net to fall on the party!')
			for p in trapped:
				p.disabled = random.randint(1, 4)
				print(p.name, 'is caught in the tar covered sticky net for %d rounds!' % p.disabled)
				#we are adding one, because we are skipped in the ambush on the first round, making it moot
				p.disabled += 1
			print('The net is covered in alarm bells that make a loud noise.')
			#trigger an ambush from the orcs in the common room
			room.room_actions.append(AmbushRoomTrigger())
			#set the monsters
			room.monsters = white_orc_ambush_party
			#if the orcs come from the common room, then we need to clear them there.
			self.common_rm.monsters = []
		return True

wh_orc_common_room = Room("White Orc Common Room", None, "A large room with torches burning on the wall. Some large crates of fruit are stacked in one corner.", "a large room.", [] , white_orc_ambush_party)

wh_orc_lair_entrance = Room("White Orc Lair Entrance", None, "The cave entrance opens up into a large cavern with wood planked floor. A large black banner with a white fist hangs prominently on the north wall.", 'the entrance to a cave. Hundreds of white, bleached skulls frame the top.', [], [], [FallingNetTrap(wh_orc_common_room)])

wh_orc_chief = Monster("Wht Orc Chieftain", "The white orc chieftain wields a large sword. He speaks with other orcs here with his back to you.", 16, [ MonsterAttack('slashes', 8) ], 35, 1, 2 )

gold_buckle = Item('Gold belt buckle', 'a gold dragon haead belt buckle', 'on the belt of the orc chieftain.', GP(50))

wh_orc_chieftains_rm = Room("White Orc Chieftain's Chamber", None, "Stacks of barrels, boxes, and sacks line the wall. The area is well furnished with a small chest of drawers and a small table next to the bed.", 'a dark chamber.', [ITEM('wine'), gold_buckle, shard3], [wh_orc_chief, Mon('Orc'), Mon('Orc')] )

########################################################
## Goblin Lair

goblin_entrance = Room("Goblin Lair Entrance", None, "This natural ragged cave opening quickly turns to finished stone walls and floor. The floor is wet and worn smooth by the pad of many feet.", "a cave entrance.")

s_goblin_guard_rm = Room("Goblin South Guard Room", None, "This chamber is full of tables and benches. Against the wall, a pile of spears lay in a heap.", 'a small chamber.', [], [ Mon('Goblin', 'These goblin guards are singing quite loudly in some unknown language. They are holding some drink that they are sloshing about as they sing.'), Mon('Goblin'), Mon('Goblin'), Mon('Goblin')])

n_goblin_guard_rm = Room("Goblin North Guard Room", None, "This chamber is full of pallets and shabby clothing hanging on pegs.", 'a small chamber.', [], [ Mon('Goblin', 'These goblin guards are dancing in a circle arm over arm. They appear to be singing a little too loud and paying too much attention to how high they can kick.'), Mon('Goblin'), Mon('Goblin'), Mon('Goblin')])

many_goblins = []
for i in range(0, 10):
	many_goblins.append(Mon('Goblin'))
many_goblins[0].description = 'Many goblins are laying on cots scattered about the room.'

goblin_common_rm = Room("Goblin Common Room", None, "There are cots and scattered bedding and piles of clothing and rubbish. Heaps of trash and rags pile near the door. The room smells of wet socks.", 'a large room.', [], many_goblins)

goblin_chief = Monster("Goblin Chieftain", "A huge goblin chieftain sits at the table, talking with some other goblins while looking at a map. He wears a necklace set with a large shining gemstone.", 11, [ MonsterAttack('slashes', 8) ], 30, 1, 4 )

goblin_chf_rm = Room("Goblin Chieftain Room", None, "This place has a good bit of furniture in it. A large table dominates the center of the room.", "a small carpeted room.", [ MAG_ITEM('Potion of Healing'), shard4 ], [ goblin_chief, Mon('Goblin'), Mon('Goblin'), Mon('Goblin') ] )

goblin_storage_rm = Room("Goblin Storage Room", None, "Stacks and heaps of supplies pack this small, cold, chamber.", 'a storage room.', [ ARMOR('Shield'), ITEM('torches'), ITEM('hard tack'), ITEM('wine'), WEAPON('Mace')], [ Mon('Goblin', 'Goblin guards sit here playing cards on a barrel. They wear fur coats and are sipping hot beverages.'), Mon('Goblin'), Mon('Goblin') ] )

########################################################
## Ogre Cave

ogre_cave_entrance = Room("Ogre Cave Entrance", "As soon as you enter this cave, you notice a strong, sour odor and see what appears to be a large bear sleeping in the side of the cave! Upon closer inspection, you see it's just the skin of bear on a bed. Water drips from the ceiling into a small pool at the side. It's very quiet here.", "A large stinky cave, with bear hid covered bed in corner.", "a dark cave entrance.")

large_ogre = Monster("Large Ogre", '''Sitting on top of a great leather bag sits a large ogre. He is counting some coins and laughing about something. "Soap! he says.. I don't need no stinking soap!" A large oaken club leans against the wall next to him.''', 25, [MonsterAttack('clubbed', 12)], 45, 1, 4)

bag_of_gold = Item("bag of gold", "many gold coins in a leather bag.", None, GP(289))

potion_of_invisbility = InvisibilityPotion("Potion of Invisibility", "a small blue vial of clear fluid.")

scroll_of_healing = HealScroll("Scroll of Healing", "a small roll of golden parchment in a silver case.", None, GP(200))

ogre_cave = Room("Ogre Hideout", None, "This small tunnel opens up into a larger cave. A single torch flickers on the wall. This room smells very strongly of ogre stench.", "a small dark tunnel.", [scroll_of_healing, bag_of_gold, potion_of_invisbility, shard5], [large_ogre])

########################################################
## Hobgoblin Lair

hobgoblin_entrance_door = Door('''a stout barred door blocks the entrance to this cave. Several skulls are affixed to the door with a warning "Come in - we'd like to have you for dinner!"''')

hobgoblin_entrance = Room("Hobgoblin Lair Entrance", None, "Skulls line the walls of this ominous cave. It is clear these inhabitants don't intend to be friendly.", "a cave entrance.")

many_hgoblins = []
for i in range(0, 10):
	many_hgoblins.append(Mon('Hobgoblin'))
many_hgoblins[0].description = 'Many hobgoblins are laying on beds scattered about the room.'

hobgoblin_common_rm = Room("Hobgoblin Common Room", None, "This large rooms is filled with sleeping skins and piles of refuse.", 'a large dark room.', [ ITEM('hard tack'), ITEM('wine'), ITEM('rope'), MAG_ITEM('Potion of Healing')], many_hgoblins)

merchant = GoodNPC('Ribald McMillini')
merchant.age = 53
merchant.roll_attr()
merchant.strength = 10
merchant.sp = 0
merchant.gp = 0
merchant.skills.append(new_skill(SKILL_CAT_SHORT_EDGE))
merchant.hp = 10
merchant.cur_hp = 10
merchant.description = 'An elderly merchant.'

lady = GoodNPC('Shelila')
lady.age = 21
lady.roll_attr()
lady.sp = 0
lady.gp = 0
lady.sex = "female"
lady.skills.append(new_skill(SKILL_CAT_SHORT_EDGE))
lady.skills.append(new_skill(SKILL_CAT_PICK_POCKET))
lady.skills.append(new_skill(SKILL_CAT_STEALTH))
lady.hp = 8
lady.cur_hp = 8
lady.description = 'A pretty lady.'

mercenary = GoodNPC('Archos')
mercenary.age = 32
mercenary.roll_attr()
mercenary.strength = 16
mercenary.sp = 0
mercenary.gp = 0
mercenary.experience = 1500
mercenary.level = 2
mercenary.skills.append(new_skill(SKILL_CAT_SHORT_EDGE))
mercenary.skills.append(new_skill(SKILL_CAT_ARMOR))
mercenary.skills.append(new_skill(SKILL_CAT_LONG_EDGE, 2))
mercenary.hp = 18
mercenary.cur_hp = 18
mercenary.description = 'A seasoned fighter.'

class CellRoomHandler(RoomTrigger):

	def __init__(self, merchant, lady, mercenary):
		self.merchant = merchant
		self.lady = lady
		self.mercenary = mercenary
		
	def do_trigger_on_won(self, room, party, level):
		return True
		
	def on_triggered(self, room, party, level):
		print('''
  The three prisoners cheer as they see their captors go down. You find the keys on the belt of the large hobgoblin and open the cell door.
		
  A chubby, older gentleman introduces himself, "Ribald McMillini at your service.", he says with a stiff bow, his back somewhat in pain. "And I thank you from the bottom of my heart! We have been locked here for an age. And only tonight these horrible creatures had planned to eat me for dinner! I can only shiver to think of that fate. For safe passage to Kendar, my guild will reward you handsomely."
		
  "And I'm Shelila." says the next captive with a curtsy. She smiles shyly. "And I too thank you for your galantry. I can not repay you now, but would gladly reward you if you were to take me to Kendar."
		
  "I too salute your bravery." says the rough, strong looking third captive. "I am called Archos. And if you would give me steel I will fight by your side as long as you see fit."
		''')
		yn = util.get_input("Would you accept Ribald into your party? (y, n) -> ")
		if yn == 'y':
			print('Ribald bows deeply. "I am forever in your debt."\n')
			party.append(self.merchant)
		yn = util.get_input("Would you accept Shelila into your party? (y, n) -> ")
		if yn == 'y':
			print('''Shelila squeels happily, "I can't wait to go home!"\n''')
			party.append(self.lady)
		yn = util.get_input("Would you accept Archos into your party? (y, n) -> ")
		if yn == 'y':
			print('Archos shakes your hand. "I am your servant."\n')
			party.append(self.mercenary)
		room.monsters = []
		return True

hgoblin_lg_cell = Room("Hobgoblin Large Cell", "This large room is dominated with a large iron bars down the center. On one side, the cots and chains to bind prisoners. And on the other, some tables and benches for their keepers. A large iron lock binds the gate in the center. In the cell are three prisoners, shackled to the wall.", "A large cell room.", "a dark steep tunnel.", [], [Mon('Hobgoblin', 'These large hobgoblin guards play cards, seated at one of the tables.'), Mon('Hobgoblin')], [CellRoomHandler(merchant, lady, mercenary)])

n_hgoblin_guard_rm = Room("Hobgoblin North Guard Room", None, "There are two cots, a bench, and a stool. Some dice and a bottle of wine are on the table.", 'a small chamber.', [], [ Mon('Hobgoblin', 'These hobgoblin guards are in a circle, cheering as two of them box bare fisted in the center.'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin')])

armory_door_key = Item("a silver key", "a key shapped like an arrow", "hangs on a peg near the doorway.")
armory_door = Door("a stout oaken door with iron bands. A sword and shield emblem is burned into the wood.", armory_door_key)

class ArmoryHandler(RoomTrigger):
	
	def __init__(self):
		self.inv = []
		s = all_armor + all_weapons
		for i in range(0, 10):
			iIt = random.randint(0, len(s) - 1)
			cp = copy.deepcopy(s[iIt])
			self.inv.append(cp)
		
	def do_trigger_on_look(self, room, party, level):
		return len(room.monsters) == 0
	
	def do_trigger_on_search(self, room, party, level):
		return len(room.monsters) == 0
	
	def on_triggered(self, room, party, level):
		if len(self.inv) == 0:
			return True
		print('There are a range of amory to choose from. Take your pick:')
		print('0\tnothing')
		for i in range(0, len(self.inv)):
			print(i + 1, '\t%s' % self.inv[i].name)
		iChoiceS = get_input('Enter number to get item -> ')
		try:
			iChoice = int(iChoiceS)
			if iChoice > 0 and iChoice <= len(self.inv):
				item = self.inv[iChoice - 1]
				divide_loot(party, [item])
				self.inv.remove(item)
		except:
			print(iChoiceS, "is not a valid choice.")
		if len(self.inv) == 0:
			room.description = 'This room is filled with empty racks.'
		return False
		
hgoblin_amory_rm = Room("Hobgoblin Armory", None, "This room is filled with armor of all shapes and sizes. Racks of weapons line the walls.", "a small room.", [], [Mon('Hobgoblin', 'These hobgoblin guards look as if they are expecting you.'), Mon('Hobgoblin'), Mon('Hobgoblin')], [ArmoryHandler()])

s_hgoblin_guard_rm = Room("Hobgoblin South Guard Room", None, "This chamber is full of tables and benches. Against the wall, a pile of wood lay in a heap.", 'a small chamber.', [armory_door_key], [ Mon('Hobgoblin', 'These hobgoblin guards are gathered around the table, shouting encouragments at two of them who are arm wrestling.'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin')])

class UnlimitedFoodLarder(RoomTrigger):
		
	def do_trigger_on_look(self, room, party, level):
		return len(room.monsters) == 0
	
	def do_trigger_on_search(self, room, party, level):
		return len(room.monsters) == 0
	
	def on_triggered(self, room, party, level):
		print("There is enough food and drink here to feed an army!")
		yn = util.get_input("Would you like to grab 10 food and water for each in your party? (y, n) -> ")
		if yn == 'y':
			for p in party:
				nf, nd = p.get_num_food_drink()
				if nf < 10 and nd < 10:
					for i in range(0, 10):
						p.add(ITEM('hard tack'))
						p.add(ITEM('water'))
			print('Everyone is loaded up with food and water!')
		return False
	
hgoblin_storage_rm = Room("Hobgoblin Storage Room", None, "Stacks and heaps of supplies pack this large, cold, chamber.", 'a storage room.', [], [ Mon('Goblin', 'A Hobgoblin guards sits here on a bench. He looks like he was just about to doze off.') ], [UnlimitedFoodLarder()] )

hgoblin_chief = Monster("Hobgoblin Chieftain", "A huge, armored, hobgoblin chieftain stands by the fireplace talking with the other hobgoblins while looking at a map.", 22, [ MonsterAttack('slashes', 13) ], 45, 1, 2 )

hgoblin_chf_rm = Room("Hobgoblin Chieftain Room", None, "This place is crowded with furniture and junk of no real value. A large fireplace dominates the end of the room. Above the mantle is the head of an owlbear, stuffed on a mount.", "a large carpeted room.", [ MAG_ITEM('Wand of Paralyzation'), shard6 ], [ hgoblin_chief, Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin'), Mon('Hobgoblin') ] )

########################################################
## Shunned Cavern

note = Item("Rotting note", "a note on rotting parchment", "clutched in the dead hand of a dwarf reads, 'Leave now, while you can!'")

shunned_cavern = Room("Shunned Cavern", None, "The odor of this place is awful. Bones and rotting corpses are spread here and there amidst a litter of dead leaves and old branches.", 'a cave entrance.', [note])

jewled_goblet = Item("jewelled goblet", "a golden jewelled goblet", 'laying in the shallows of the water.', GP(130))

shallow_pool = Room("Shallow Pool", None, "This portion of the cavern is very wet, and the walls and floor have a sheen from the dampness. There's a large pool of shallow water here, and a few white, blind fish are swimming around.", "a shallow pool.", [jewled_goblet], [Mon('Grey Ooze', 'You discover a weird slimy gooey creature, stuck to the cieling. There appears to be many of them.'), Mon('Grey Ooze'), Mon('Grey Ooze')])

fb_scroll = MAG_ITEM('Fireball Scroll')
fb_scroll.location = 'hidden in the rotting bag of a dead wizard.'
fb_scroll.description = fb_scroll.description[:-1] #less the period

owlbears_den = Room("Owlbears Den", None, "This cave smells foul and reeks even more than the entrance. More piles of bones are littered about in unorganized piles.", "a foul, dark cavern.", [fb_scroll], [Mon("Owlbear", "A huge owlbear snacks on a gnoll it captured earlier. It crunches the bones loudly. It roars as it sees you coming, it's ferocious toothy beak opening large and snarling. Two huge paws claw the air as it raises its large bulk on two hind legs.")])

########################################################
## Bugbears Lair

bugbear_entrance = Room("Bugbear Lair Entrance", None, "This cave opening is quite finished, opening onto smooth stone walls and floor. There are signs by the entrance in kobold, orcish, goblin, and common which read: 'Welcome! Come in and report to the first guard on the left for a hot meal and a bed assignment.'", "a cave entrance.")

silver_urn = Item("silver urn", "a small, ornate, sliver urn", "somewhat blacked by soot and sitting near the fire.", GP(175))

bugbear_common_rm = Room("Bugbear Common Room", None, "This room is full of piles of bedding and old garments. There is a central fire pit, blacked by soot, with a pot hanging above.", "a room full of bedding.", [silver_urn], [Mon("Bugbear"),Mon("Bugbear"),Mon("Bugbear"),Mon("Bugbear")])

class BugbearTrick(RoomTrigger):
	def __init__(self):
		self.offered = False
		self.ambushed = False
		
	def do_trigger_on_enter(self, room, party, level):
		return True
		
	def do_trigger_fight(self, room, party, level):
		if self.offered and not self.ambushed:
			util.get_input('The bugbears suddenly jump up and attack you! One hits the gong hard, causing a loud sound. More bugbears rush into the room from the west. Hit return to continue.')
			self.ambushed = True
			for m in bugbear_common_rm.monsters:
				room.monsters.append(m)
			bugbear_common_rm.monsters = []
			return True
		return False
		
	def on_triggered(self, room, party, level):
		if not self.offered:
			yn = util.get_input( 'One bugbear offers you skewer of meat, "Welcome friends! Would you like to sit and have some meat?" (y, n) -> ' )
			if yn == 'y':
				print("One bugbear hands you a skewer of meat. It's lightly salted and quite yummy!")
			else:
				print("The bugbear scowls and throws down the meat.")
			self.offered = True
		return self.ambushed

bugbear_guard_rm = Room("Bugbear Guard Room", None, "Stools and tables sit next to a large smoking brazier, which has skewers of meat roasting over the coals. There are two cots and a large gong against one wall.", 'another guard room.', [], [ Mon("Bugbear", "These creatures lounge on the stools near the smoking brazier."), Mon("Bugbear"), Mon("Bugbear") ], [BugbearTrick()])

bugbear_chieftain = Monster("Bugbear Chieftain", "A tough old bugbear chieftain sits in a large chair, talking with some other bugbears. He wears a necklace set with a large shining gemstone.", 18, [ MonsterAttack('slashes', 13) ], 30, 1, 4 )

bugbear_chieftain_rm = Room("Bugbear Chieftain Room", None, "The furnishings of the room are battered and crude.", "a chieftain room.", [MAG_ITEM("Potion of Healing"), shard7], [ bugbear_chieftain, Mon("Bugbear"), Mon("Bugbear"), Mon("Bugbear"), Mon("Bugbear") ])

cellDoorKeyA = Item("cell block key", "a large iron key", "on the keyring attached to the bugbears waist.")

cellDoorA = Door("a large, rusted iron door with small grill opening.", cellDoorKeyA)

cellDoorKeyB = Item("cell block key", "a large iron key", "on the keyring attached to the bugbears waist.")

cellDoorB = Door("a large, rusted iron door with small grill opening.", cellDoorKeyB)

bugbear_long_hallway = Room("Bugbear Cellblock Hallway", None,
							'''
	A long hallway runs down straight into the cliff side. Its looks like it was tunnelled very roughly. Doors flank either side and you can hear shouts and moans in the distance.
	In the center of the hallway, is a large circular wooden table, with guards sitting there.''',
							"a long hallway.", [cellDoorKeyA, cellDoorKeyB], [Mon("Bugbear", 'They stand as they see you enter, "Hey!! Who goes there?!", they shout.'), Mon("Bugbear"), Mon("Bugbear"), Mon("Bugbear") ])

class BBCellRoomHandler(RoomTrigger):

	def __init__(self, freed, detained):
		self.freed = freed
		self.detained = detained
		
	def do_trigger_on_enter(self, room, party, level):
		return True
		
	def on_triggered(self, room, party, level):
		print("Just inside the cell you see a lockbox. A quick kick and it's open. You can see the large ring of keys on it.")
		yn = util.get_input("Would you unlock the chains of the prisoners? (y, n) -> ")
		if yn == 'y':
			print(self.freed)
			return True
		else:
			print(self.detained)
		return False

bbCellA = BBCellRoomHandler('''The prisoners cheer weakly, "Yaaay! Huzah!!",  There are orcs, humans, gnolls, a dwarf, and two elves locked up here. Not sure what to do with their newfound freedom, some pause.
	After one of the orcs runs for the door, there is a stampede to follow him. The dwarf tips his head and smiles to you.''', '''As a group they howl at you, "How can you let us rot here!!!"''')

bugbear_cellblock_a = Room("Bugbear Cell Block A", "This long room is full of long, rough hewn wooden benches. Piles of straw and rags look like bedding for the residents. Countless creatures are chained along the wall with only a short length of chain for movement.",
						   "A long room full of rough benches and shackles on the wall.", "a prison cell.", [], [] , [bbCellA])

bbCellB = BBCellRoomHandler('''The prisoners have little reaction. They are stunned by their sudden freedom. The large ogres don't seem to have the energy to stand. But after the group of dwarves leaves, they get up to follow.''',
							'''Their tiredness and sadness only deepens. They turn away.''')

bugbear_cellblock_b = Room("Bugbear Cell Block B", "This room has one long, rough hewn wooden bench along the wall. Two large ogres are chained here, looking very skinny, drawn, and weak. And further down, a group of dwarves is chained.",
						   "A long room full of rough benches and shackles on the wall.", "a prison cell.", [], [] , [bbCellB])

########################################################
## Level definition

test_rm = Room("A room", "what you see the first time", "what you see the rest of the time", "this is what you see when one room away")

########################################################
## Level definition

level1 = Level ("Caves of Chaos", level_banner)

#checks for the completion of the level
level1.add_level_logic( CavesLevelLogic() )

#in-town
inn.connect("North", main_road)
main_road.connect("West", shop)
main_road.connect("East", temple)
main_road.connect("North", forrest)

#in the forest and swamp
forrest.connect("West", spiders_lair)
spiders_lair.connect("West", mad_hermit_hollow)
forrest.connect("East", swamp_trail)
swamp_trail.connect("East", lizard_men_mounds)

#Caves of Chaos ravine
forrest.connect("North", ravine)
ravine.connect("North", ravine_floor)
ravine_floor.connect("North", ravine_end)
ravine_floor.connect("West", trail_mw)

ravine.connect("East", trail_a)
ravine.connect("West", trail_w)
trail_a.connect("South", upper_trail_a)

ravine_end.connect("North", n_trail) #-> Shunned Cavern
n_trail.connect("West", nw_mid_trail) #-> Bugbear Lair
n_trail.connect("East", ne_mid_trail) #-> Caves of Minotaur
nw_mid_trail.connect("West", nw_upper_trail) #-> Shrine of Evil Chaos

#Kobold Lair
trail_a.connect("East", kobolds_lair)
kobolds_lair.connect("North", entrance_trap)
entrance_trap.connect("West", kob_guard_room)
entrance_trap.connect("East", kob_elite_guard)
kob_elite_guard.connect("North", rat_lair)
kob_elite_guard.connect("South", kob_chieftain_rm)
kob_elite_guard.connect("East", kob_common_chamber)
kob_chieftain_rm.connect("East", kob_food_storage, kob_food_door)

#Red Orc Lair
upper_trail_a.connect("East", orc_lair_entrance)
orc_lair_entrance.connect("South", orc_guard_rm)
orc_lair_entrance.connect("North", orc_banquet_rm)
orc_banquet_rm.connect("North", orc_common_rm)
orc_banquet_rm.connect("East", orc_leaders_rm)
orc_guard_rm.connect("South", orc_storage_rm, orc_storage_door)

#White Orc Lair
upper_trail_a.connect("South", upper_trail_b)
upper_trail_b.connect("East", wh_orc_lair_entrance )
wh_orc_lair_entrance.connect("North", wh_orc_common_room)
wh_orc_lair_entrance.connect("South", wh_orc_chieftains_rm)

#Goblin Lair
trail_w.connect("West", goblin_entrance)
goblin_entrance.connect("North", n_goblin_guard_rm)
goblin_entrance.connect("South", s_goblin_guard_rm)
s_goblin_guard_rm.connect("West", goblin_common_rm)
n_goblin_guard_rm.connect("West", goblin_chf_rm)
n_goblin_guard_rm.connect("North", goblin_storage_rm)

#Ogre Cave
trail_w.connect("South", upper_trail_c)
upper_trail_c.connect("West", ogre_cave_entrance)
ogre_cave_entrance.connect("West", ogre_cave)

#Hobgoblin Lair
trail_mw.connect("West", hobgoblin_entrance, hobgoblin_entrance_door)
hobgoblin_entrance.connect("North", n_hgoblin_guard_rm)
n_hgoblin_guard_rm.connect("North", hgoblin_lg_cell)
hobgoblin_entrance.connect("South", s_hgoblin_guard_rm)
hobgoblin_entrance.connect("West", hgoblin_amory_rm, armory_door)
s_hgoblin_guard_rm.connect("South", hgoblin_chf_rm)
hgoblin_chf_rm.connect("South", hgoblin_storage_rm)

#Shunned Cavern
n_trail.connect("North", shunned_cavern)
shunned_cavern.connect("North", shallow_pool)
shallow_pool.connect("North", owlbears_den)

#Bugbear Lair
nw_mid_trail.connect("North", bugbear_entrance)
bugbear_entrance.connect("North", bugbear_guard_rm)
bugbear_guard_rm.connect("West", bugbear_common_rm)
bugbear_guard_rm.connect("East", bugbear_chieftain_rm)
bugbear_guard_rm.connect("North", bugbear_long_hallway)
bugbear_long_hallway.connect("West", bugbear_cellblock_a, cellDoorA)
bugbear_long_hallway.connect("East", bugbear_cellblock_b, cellDoorB)

run_adventure(level1, inn)



