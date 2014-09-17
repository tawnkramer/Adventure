from items import *
from spells import *
from scrolls import *
from potions import *
from wands import *

##############################################
## Items

all_items = [
	Food('hard tack', 'rations made to last long and fill the belly.', None, GP(1)),
	Food('bread', 'a crusty loaf of bread. slightly hard on the ends.', None, GP(1)),
	Drink('water', 'a skin of water.', None, GP(1)),
	Drink('wine', 'a skin of cheap barely wine.', None, GP(1)),
	Item('lock pick set', 'a set of slivers of metal and hooks, ideal for exploring a lock.', None, GP(25), SKILL_CAT_LOCK_PICK),
	Item('rope', 'a 50 foot length of strong rope.', None, GP(1)),
	Item('torches', 'a set of 6 torches while light for 100 rounds.', None, GP(1)),
	Item('tinder box', 'a flint and steel set for lighting fires.', None, GP(3)),
	Item('backpack', 'a large leather pack.', None, GP(5)),
	Item('Holy Symbol', 'a relic of the chosen gods.', None, GP(25)),
	Item('lantern', 'a glass and copper tube with oil, providing light for 500 rounds.', None, GP(10)),
	Item('iron spikes', 'a set of 12 iron spikes, suitable for aid in climbing or other uses.', None, GP(10)),
	Food('dried meat', 'a dry pices of meat, salty yet satisfying.', None, GP(1)),
]


def ITEM(name):
	for i in all_items:
		if i.name == name:
			return copy.deepcopy(i)
	return None

##############################################
## Weapons

all_weapons = [
	Weapon('Quarterstaff', 'a long wooden staff, stout yet flexible.', 4, 'whacks', GP(4), SKILL_CAT_ANY ),
	Weapon('Dagger', 'a small slender blade, fast and light.', 4, 'jabs', GP(3), SKILL_CAT_ANY ),
	Weapon('Elvish Dagger', 'a fine slender blade, fast and light.', 6, 'jabs', GP(130), SKILL_CAT_ANY ),
	Weapon('Hand Axe', 'a small axe balance nicely for combat.', 4, 'hacks', GP(4), SKILL_CAT_SHORT_EDGE ),
	Weapon('War Hammer', 'a large blunt mallet for dealing cruel blows.', 6, 'slams', GP(5), SKILL_CAT_SHORT_EDGE ),
	Weapon('Mace', 'a large blunt metal cudgel for dealing smashing blows.', 6, 'smashes', GP(5), SKILL_CAT_SHORT_EDGE ),
	Weapon('Short Sword', 'a small silver blade with leather wrapped hilt, nicely balanced and very sharp.', 6, 'slashes', GP(7), SKILL_CAT_SHORT_EDGE ),
	Weapon('Elvish Short Sword', 'a fine silver blade with dragon hide hilt, amazingly balanced and sharp.', 8, 'slashes', GP(170), SKILL_CAT_SHORT_EDGE ),
	Weapon('Normal Sword', 'a long blade with leather wrapped hilt, nicely balanced and very sharp.', 8, 'slashes', GP(20), SKILL_CAT_LONG_EDGE ),
	Weapon('Two-handed Sword', 'a super long blade made for splitting anything into two.', 10, 'slashes', GP(55), SKILL_CAT_LONG_EDGE ),
	Weapon('Vorpal Two-handed Sword', 'a super long vorpal blade.', 12, 'slashes', GP(175), SKILL_CAT_LONG_EDGE ),
	Weapon('Admantium Two-handed Sword', 'a super long admantium blade, able to cut through stone.', 14, 'slashes', GP(395), SKILL_CAT_LONG_EDGE ),
	Weapon('Two-handed Battle Axe', 'a two handed brute, double edged and long.', 8, 'hacks', GP(17), SKILL_CAT_LONG_EDGE ),
	Weapon('Dwarven Two-handed Battle Axe', 'a fine two handed axe, double edged and razor sharp.', 10, 'hacks', GP(250), SKILL_CAT_LONG_EDGE ),
	Weapon('Long Bow', 'a large yew bow, too stiff for ordinary men to draw.', 6, 'shoots', GP(5), SKILL_CAT_MISSILE ),
	Weapon('War Bow', 'a large bow, powerful and flexible.', 7, 'shoots', GP(75), SKILL_CAT_MISSILE ),
	Weapon('Elvish Long Bow', 'a fine silver bow, amazingly comfortable and accurate.', 10, 'shoots', GP(300), SKILL_CAT_MISSILE ),
]
		
def WEAPON(name):
	for i in all_weapons:
		if i.name == name:
			return copy.deepcopy(i)
	return None

##############################################
## Armor
		
all_armor = [
	Armor('Leather Armor', 'a coat of hardened leather - AC 8.', GP(40), 8),
	Armor('Studed Armor', 'a leather jerkin covered with metal studs - AC 7.', GP(90), 7),
	Armor('Scale Mail Armor', 'a coat of tiny, overlapping metal plates, like fish scales - AC 6.', GP(140), 6),
	Armor('Chain Mail Armor', 'a coat of tiny silver interlocked steel rings, tough but flexible - AC 5.', GP(220), 5),
	Armor('Splint Mail Armor', 'a coat of overlapping metal slats - AC 4.', GP(300), 4),
	Armor('Plate Mail Armor', 'a shell of interlocked hardened steel plates - AC 3.', GP(390), 3),
	Armor('Shield', 'a metal studed shield - improves AC 1.', GP(25), 1, SKILL_CAT_SHIELD),
]

def ARMOR(name):
	for i in all_armor:
		if i.name == name:
			return copy.deepcopy(i)
	return None

##############################################
## Spells

all_spells = [
	#Magic User Spells
	#1st level
	OffSpell('Magic Missile', 'a red bolt of energy shoots from the finger tips blasting one target.', GP(20), 4, 2, SKILL_CAT_SPELL),
	OffSpell('Shocking Grasp', 'electicity jolts the target touched.', GP(55), 8, 3, SKILL_CAT_SPELL),
	DisableSpell('Charm Person', 'target will believe the caster is his best friend for 10 rounds.', GP(30), 0, 3, SKILL_CAT_SPELL, 10),
	DisableGroupSpell('Light', 'a blast of light blinds all creatures in the area for 3 rounds.', GP(50), 0, 5, SKILL_CAT_SPELL, 3),
	DisableGroupSpell('Sleep', 'put multiple creatures to sleep in the area for 5 rounds.', GP(85), 0, 5, SKILL_CAT_SPELL, 5),
	ShieldSpell('Shield', 'a magical barrier surrounds the caster giving them protection for 3 rounds per level.', GP(30), 0, 1, SKILL_CAT_SPELL, 3 ),
	GroupOffSpell('Burning Hands', 'shoots a sheet of fire of fire. 1 pt damage per level affecting all enemies.', GP(50), 1, 2, SKILL_CAT_SPELL),
	
	#2nd level
	InvisibilitySpell('Invisibility', 'the target vanishes. They will reappear only when they attack again.', GP(150), 0, 6, SKILL_CAT_SPELL),
	KnockSpell('Knock', 'one locked door will be opened.', GP(180), 0, 8, SKILL_CAT_SPELL),
	
	#3rd level
	GroupOffSpell('Fireball', 'a missile exploding in a ball of fire affects all enemies.', GP(370), 6, 12, SKILL_CAT_SPELL),
	LevelMultOffSpell('Lightning Bolt', 'a bolt of lightning shoots at the target. damage mult by level.', GP(340), 6, 11, SKILL_CAT_SPELL),
	
	#Healer/Clerical Spells
	#1st level
	HealSpell('Cure Light Wounds', 'heals damage to one person.', GP(20), 10, 3, SKILL_CAT_HEALER),
	DisableGroupSpell('Holy Light', 'blasts light blinding all creatures in the area for 3 rounds.', GP(50), 0, 3, SKILL_CAT_HEALER, 3),
	ShieldSpell('Protection', 'emits a glowing aura surrounding the caster, protecting them for 6 rounds.', GP(30), 0, 2, SKILL_CAT_HEALER, 6 ),
	
	#2nd level
	BlessSpell('Bless', 'energize friends, each gaining extra strength in combat. Duration depends on level.', GP(80), 0, 8, SKILL_CAT_HEALER),
	HealSpell('Cure Med Wounds', 'heals damage to one person.', GP(60), 20, 5, SKILL_CAT_HEALER),
	ScareSpell('Condemnation', 'summons the aura of their chosen god, which can strike fear in enemies.', GP(150), 0, 10, SKILL_CAT_HEALER),
	OffSpell('Word of Smite', 'a force of will blasting one target.', GP(100), 10, 2, SKILL_CAT_HEALER),
	DisableSpell('Whipser of Sha-Ren', 'target will be frozen for 10 rounds.', GP(120), 0, 3, SKILL_CAT_HEALER, 10),
	
	#3rd level
	HealGroupSpell('Healing Aura', 'heals damage to entire party. mult by level', GP(260), 10, 11, SKILL_CAT_HEALER),
	GroupOffSpell("Odin's Clap", 'a thunderous clap affecting all enemies.', GP(240), 6, 11, SKILL_CAT_HEALER),
	LevelMultOffSpell('Word of Truth', 'a force of truth blasting one target. damage mult by level.', GP(300), 10, 12, SKILL_CAT_HEALER),
	CreateFoodSpell('Create Food & Water', 'creates 3 units of food & water per level of caster.', GP(220), 0, 4,SKILL_CAT_HEALER), 
	
	#4th level
	
	#7th level
	ResurrectionSpell('Resurrection', 'bring back to life any person beyond normal healing.', GP(30000), 0, 40, SKILL_CAT_HEALER),
	
]

##############################################
## Magic Items

magic_items = [
	MagicWeapon('Dagger +1', 'a magic slender blade, fast and light', 4, 'jabs', GP(750), SKILL_CAT_ANY, None, 1, 1 ),
	MagicWeapon('Golden Short Sword + 1', 'a magic golden blade with silver wrapped hilt. nicely balanced and razor sharp.', 8, 'slashes', GP(3000), SKILL_CAT_SHORT_EDGE, None, 1, 1 ),
	
	MagicArmor('Ring of Protection', 'a magic silver ring', GP(10000), 1, SKILL_CAT_ANY),
	MagicArmor('Bracers of Defense', 'a magic arm gaurd giving armor class 4', GP(3000), 4, SKILL_CAT_ANY),
	
	MagicItem('Ring of Regeneration', 'a magic ring heals one hp per round, even bring back from the dead.', None, GP(40000)),
	MagicItem('Flask of Plenty', 'a magic drink which never runs dry, and give sustenance as food.', None, GP(3000)),
	
	HealingPotion('Potion of Healing', 'a magic drink which heals the imbiber.', None, GP(200)),
	InvisibilityPotion('Potion of Invisibility', 'a magic drink which cause you to disappear.', None, GP(250)),
	
	InvisibilityScroll('Scroll of Invisiblity', 'scroll, like the spell may target anyone in your party.', None, GP(300)),
	HealScroll('Scroll of Healing', 'scroll, like the spell may target anyone in your party.', None, GP(250)),
	BlessScroll('Scroll of Blessings', 'scroll, like the spell, strengthens whole party.', None, GP(350)),
	KnockScroll('Knock Scroll', 'scroll, like the spell, blows out any locked door.', None, GP(450)),
	FireBallScroll('Fireball Scroll', 'scroll, like the spell, casts fire blasting all enemies.', None, GP(550)),
	
	WandOfParalyzation('Wand of Paralyzation', 'a slim wand, can disable any single enemy, has limited charges.', None, GP(1000)),
]
 
def MAG_ITEM(name):
	for i in magic_items:
		if i.name == name:
			return copy.deepcopy(i)
	return None
