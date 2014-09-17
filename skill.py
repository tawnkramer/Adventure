import copy
import random

#Skill categories
#These take the place of the normal class system.
#They affect which weapons and spells you can use,
#and are upgradable at each level with skill points
#to spend in any category. At each stage you have
#the opportunity to create a stronger specialist,
#or diversify into a generalist.
SKILL_CAT_ANY = 0
SKILL_CAT_SPELL = 1
SKILL_CAT_LONG_EDGE = 2
SKILL_CAT_SHORT_EDGE = 3
SKILL_CAT_MISSILE = 4
SKILL_CAT_SHIELD = 5
SKILL_CAT_HEALER = 6
SKILL_CAT_PICK_POCKET = 7
SKILL_CAT_STEALTH = 8
SKILL_CAT_LOCK_PICK = 9
SKILL_CAT_ARMOR = 10

def get_skill_str(skill_cat):
	if skill_cat == SKILL_CAT_ANY:
		return 'Any'
	if skill_cat == SKILL_CAT_SPELL:
		return 'Spell Casting'
	if skill_cat == SKILL_CAT_LONG_EDGE:
		return 'Long Edged Weapons'
	if skill_cat == SKILL_CAT_SHORT_EDGE:
		return 'Short Edged Weapons'
	if skill_cat == SKILL_CAT_MISSILE:
		return 'Missle Weapons'
	if skill_cat == SKILL_CAT_SHIELD:
		return 'Shield Training'
	if skill_cat == SKILL_CAT_HEALER:
		return 'Healer Spell Casting'
	if skill_cat == SKILL_CAT_PICK_POCKET:
		return 'Pick Pocket'
	if skill_cat == SKILL_CAT_STEALTH:
		return 'Stealth'
	if skill_cat == SKILL_CAT_LOCK_PICK:
		return 'Lock Pick'
	if skill_cat == SKILL_CAT_ARMOR:
		return 'Armor training'
	return 'Unknown'

class Skill(object):
	def __init__(self, name, description, cost, cat, level):
		self.name = name
		self.description = description
		self.cost = cost
		self.cat = cat
		self.level = level

	def uses_mana(self):
		return self.cat == SKILL_CAT_SPELL or self.cat == SKILL_CAT_HEALER
		
all_skills = [
	Skill('long edged weapon', '\ttraining in use of swords', 3, SKILL_CAT_LONG_EDGE, 1),
	Skill('short edged weapon', '\ttraining in use of daggers and short swords', 1, SKILL_CAT_SHORT_EDGE, 1),
	Skill('missile weapon', '\t\ttraining in use of bows, javelins, and spears', 1, SKILL_CAT_MISSILE, 1),
	Skill('armor', '\t\t\ttraining in use of armor', 1, SKILL_CAT_ARMOR, 1),
	Skill('shield', '\t\t\ttraining in use of shield', 1, SKILL_CAT_SHIELD, 1),
	Skill('spell casting', '\t\ttraining in use of magic spells', 4, SKILL_CAT_SPELL, 1),
	Skill('healer', '\t\t\ttraining in use of healing arts', 3, SKILL_CAT_HEALER, 1),
	Skill('pick pocket', '\t\ttraining in pick pocketing', 1, SKILL_CAT_PICK_POCKET, 1),
	Skill('stealth', '\t\ttraining in moving quietly and hiding in shadows', 1, SKILL_CAT_STEALTH, 1),
	Skill('lock pick', '\t\ttraining in picking locks', 1, SKILL_CAT_LOCK_PICK, 1),
]

def new_skill(cat, level=1):
	for s in all_skills:
		if s.cat == cat:
			cp = copy.deepcopy(s)
			cp.level = level
			return cp
	return None
	