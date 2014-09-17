import random
import util

##################################################
## Personality Traits

BRAVE 		= 'brave'
COWARDLY 	= 'cowardly'
SERIOUS		= 'serious'
SILLY		= 'silly'
HONEST		= 'honest'
SNEAKY		= 'sneaky'
CLEVER		= 'clever'
FOOLISH		= 'foolish'
POLITE		= 'polite'
SARCASTIC	= 'sarcastic'
LOYAL		= 'loyal'
UNRELIABLE	= 'unreliable'
GENEROUS	= 'generous'
GREEDY		= 'greedy'
HUMBLE		= 'humble'
PROUD		= 'proud'
PATIENT		= 'patient'
IMPATIENT	= 'impatient'
		
traits = {BRAVE : 1,
		COWARDLY : 2,
		SERIOUS : 3,
		SILLY : 4,
		HONEST : 5,
		SNEAKY : 6,
		CLEVER : 7,
		FOOLISH : 8,
		POLITE : 9,
		SARCASTIC : 10,
		LOYAL : 11,
		UNRELIABLE : 12,
		GENEROUS : 13,
		GREEDY : 14,
		HUMBLE : 15, 
		PROUD : 16,
		PATIENT : 17,
		IMPATIENT : 18}

#opposites paired, so you can only have one of a pair
trait_pairs = [ [BRAVE, COWARDLY],
			   [SERIOUS, SILLY],
			   [HONEST, SNEAKY],
			   [CLEVER, FOOLISH],
			   [POLITE, SARCASTIC],
			   [LOYAL, UNRELIABLE],
			   [GENEROUS, GREEDY],
			   [HUMBLE, PROUD],
			   [PATIENT, IMPATIENT],
			]
			
#Get a random trait, positive or negative
#and make sure you don't repeat either existing traits or
#it's opposite.
def get_random_trait(positive, existing):
	found = False
	while not found:
		iA = random.randint(0, len(trait_pairs) - 1)
		if positive:
			a = trait_pairs[iA][0]
			opp = trait_pairs[iA][1] 
		else:
			a = trait_pairs[iA][1]
			opp = trait_pairs[iA][0]
		if opp not in existing and a not in existing:
			existing.append(a)
			found = True

#global subject id
g_subject_id = 0

#get next subject id and increment
def subj_id():
	global g_subject_id
	g_subject_id += 1
	return g_subject_id

##############################################################
# subjects
# These token are replaced in the comment
# with some value taken from the environment

SPEAKER 				= subj_id()
SPEAKER_PRONOUN			= subj_id()
PARTY_MEM 				= subj_id()
PARTY_MEM_PRONOUN		= subj_id()
PARTY_MEM_DEAD			= subj_id()
MON_NAME_PLURAL 		= subj_id()
MON_NAME_SINGULAR		= subj_id()
MON_COUNT 				= subj_id()
JUST_DIED				= subj_id()

##############################################################
# Subject handlers, These return string value for subject id
# or None if can't determine.

def get_speaker(speaker, env):
	return speaker.name

def get_speaker_pronoun(speaker, env):
	return speaker.get_pronoun_lower()

def get_party_mem(speaker, env):
	for p in env.party:
		if p.is_alive() and p is not speaker:
			return p.name
	raise Exception('none found')
	
def get_party_mem_pronoun(speaker, env):
	for p in env.party:
		if p.is_alive() and p is not speaker:
			return p.get_pronoun_lower()
	raise Exception('none found')
	
def get_dead_party_mem(speaker, env):
	for p in env.party:
		if not p.is_alive() and p is not speaker:
			return p.name
	raise Exception('none found')
	
def get_monster_name_plural(speaker, env):
	if len(env.monsters) > 1:
		return (env.monsters[0].name.lower() + 's')
	raise Exception('none found')
	
def get_monster_name_singular(speaker, env):
	if len(env.monsters) > 0:
		return (env.monsters[0].name.lower())
	raise Exception('none found')

def get_monster_count(speaker, env):
	if len(env.monsters) > 1:
		return str(len(env.monsters))
	raise Exception('none found')
	
def get_just_died(speaker, env):
	return env.level.combat_stats.just_died.name
	
##############################################################
# associate subjects with their handlers
# this can be extended on a per adventure basis

subj_handlers = {
	SPEAKER 			: get_speaker,
	SPEAKER_PRONOUN		: get_speaker_pronoun,
	PARTY_MEM 			: get_party_mem,
	PARTY_MEM_PRONOUN 	: get_party_mem_pronoun,
	PARTY_MEM_DEAD 		: get_dead_party_mem,
	MON_NAME_PLURAL		: get_monster_name_plural,
	MON_NAME_SINGULAR	: get_monster_name_singular,
	MON_COUNT			: get_monster_count,
	JUST_DIED			: get_just_died,
}
			
##############################################################
## Sitch

#global sitch id
g_sitch_id = 0

#get next subject id and increment
def sitch_id():
	global g_sitch_id
	g_sitch_id += 1
	return g_sitch_id
	
RETREATED = 'retreated'
DIED = 'died'
WON = 'won'
	
sitch_dict = {
	DIED : sitch_id(),
	RETREATED : sitch_id(),
	WON : sitch_id(),
	}
	
def SITCH(sitch_str):
	return sitch_dict[sitch_str]
	
def TRAIT(trait_str):
	return traits[trait_str]
			
class CommentEnv(object):
	def __init__(self, party, room, monsters, level, sitch):
		self.party = party
		self.room = room
		self.monsters = monsters
		self.level = level
		self.sitch = sitch
			
class Comment(object):
	def __init__(self, text, replacables, traits, sitch):
		self.text = text
		self.replaceables = replacables
		self.traits = []
		self.sitch = []
		for t in traits:
			self.traits.append(TRAIT(t))
		for s in sitch:
			self.sitch.append(SITCH(s))
		
	def get_sitch_score(self, sitch):
		score = 0
		for s in sitch:
			if s in self.sitch:
				score += 1
		return score
		
	def get_trait_score(self, traits):
		score = 0
		for t in traits:
			if t in self.traits:
				score += 1
		return score
		
	def get_best_player(self, env):
		ps = 0
		player = None
		for p in env.party:
			if not p.is_alive():
				continue
			_ps = self.get_trait_score(p.traits)
			if _ps > ps:
				ps = _ps				
				player = p
		if player is None:
			iPlayer = random.randint(0, len(env.party) - 1)
			player = env.party[iPlayer]
			if not player.is_alive():
				player = None
		#if util.DEBUG and player is not None:
		#	print player.name, ps, self.text
		return [player, ps]
		
	def score(self, env):
		s = self.get_sitch_score(env.sitch)
		if s == 0:
			return [0, 0]
		player, ps = self.get_best_player(env)
		try:
			self.get_replaceables(player, env)
		except:
			return [0, 0]
		return [s, s + ps]
		
	def get_replaceables(self, speaker, env):
		global subj_handlers
		subs = []
		for rep in self.replaceables:
			handler = subj_handlers[rep]
			token = handler(speaker, env)
			if token is not None and isinstance(token, str):
				subs.append(token)
			else:
				raise Exception('Token not found for' + str(rep))
		return tuple(subs)
		
	def develop(self, env):
		player, ps = self.get_best_player(env)
		subs = self.get_replaceables(player, env)
		return self.text % subs
		
class CommentaryEngine(object):
	def __init__(self):
		self.comments = []
		
	def add(self, comment):
		self.comments.append(comment)
		
	def comment(self, env, thresh=1):
		best = []
		for c in self.comments:
			sitch_score, comb_score = c.score(env)
			if sitch_score == len(c.sitch):
				best.append([c, comb_score])
			
		#did any comments make our cut-off?
		if len(best) == 0:
			return None
			
		#sort by score
		best.sort(key=lambda comment: comment[1])
		
		#if util.DEBUG:
		#	for c in best:
		#		print c[1], c[0].text
		
		#just the best now. maybe random choice of top N in future?
		best_score = best[-1][1]
		best_group = []
		for cm in best:
			if cm[1] == best_score:
				best_group.append(cm[0])
				
		if len(best_group) == 1:
			best_comment = best_group[0]
		else:
			iB = random.randint(1, len(best_group) - 1)
			best_comment = best_group[iB]
		
		#comment text
		try:
			c = best_comment.develop(env)
		except:
			return None
		
		#remove the comment as a candidate in the future
		self.comments.remove(best_comment)
		
		#return text to be displayed
		return c
		
		
##################################
# comment engine

ce = CommentaryEngine()

#############################
## Retreated

ce.add(Comment('%s stops running and turns to %s, "Are you ok, %s? Those %s %s were nasty!"', [SPEAKER, PARTY_MEM, PARTY_MEM, MON_COUNT, MON_NAME_PLURAL], [POLITE, HONEST, SERIOUS], [RETREATED]))

ce.add(Comment('%s pants, "What the heck?! Those %s were scary!"', [SPEAKER, MON_NAME_PLURAL], [COWARDLY, HONEST, SERIOUS], [RETREATED]))

ce.add(Comment('%s stops, panting hard, "If I never see another %s, it will be too soon!"', [SPEAKER, MON_NAME_SINGULAR], [COWARDLY, HONEST, SERIOUS], [RETREATED]))

ce.add(Comment('%s stops to catch %s breath. "Whew, where do all these %s come from!"', [SPEAKER, SPEAKER_PRONOUN, MON_NAME_PLURAL], [COWARDLY, SARCASTIC, SNEAKY], [RETREATED]))

ce.add(Comment('%s stops running. "Whose idea was it to run, anyway? I was having a good fight!"', [SPEAKER], [PROUD, SARCASTIC, IMPATIENT], [RETREATED]))

ce.add(Comment('%s huffs with a frown, "Not again! We always run."', [SPEAKER], [HONEST, SERIOUS, SARCASTIC, IMPATIENT], [RETREATED]))

ce.add(Comment('''%s says, "That's not fair! I wanted to keep fighting."''', [SPEAKER], [PROUD, IMPATIENT], [RETREATED]))

ce.add(Comment('''%s says, "Wow, we are so brave."''', [SPEAKER], [SARCASTIC], [RETREATED]))

ce.add(Comment('''%s says, "Umm, why did we stop running? Let's get out of here!!!!"''', [COWARDLY, SPEAKER], [SILLY], [RETREATED]))

ce.add(Comment('''%s says, "Let's go back for the gold!"''', [SPEAKER], [GREEDY], [RETREATED]))

ce.add(Comment('''%s stops running, panting, "Ok, let's not do that again."''', [SPEAKER], [LOYAL], [RETREATED]))

ce.add(Comment('''%s says, "I ... almost had them."''', [SPEAKER], [UNRELIABLE], [RETREATED]))

ce.add(Comment('''%s says, "No! No! No! I wanna go back!"''', [SPEAKER], [BRAVE], [RETREATED]))

ce.add(Comment('''%s says, "We almost had them!"\n%s laughs, "Or not!"''', [SPEAKER, PARTY_MEM], [BRAVE], [RETREATED]))

#############################
## Player just died

ce.add(Comment('''%s screams, "Nooooo! Not %s!"''', [SPEAKER, JUST_DIED], [LOYAL], [DIED]))

ce.add(Comment('''%s screams, "%s!!!"''', [SPEAKER, JUST_DIED], [HONEST, SERIOUS], [DIED]))

ce.add(Comment('''%s screams, "This is way too scary! Let's get out of here!"''', [SPEAKER], [COWARDLY, UNRELIABLE], [DIED]))

ce.add(Comment('''%s screams, "I want to go home!"''', [SPEAKER], [SILLY, COWARDLY], [DIED]))

ce.add(Comment('''%s screams, "Retreat!"''', [SPEAKER], [HONEST, LOYAL], [DIED]))

#############################
## Player just died and retreated

ce.add(Comment('''%s cries, "Let's get you to a priest, %s!"''', [SPEAKER, JUST_DIED], [LOYAL], [RETREATED, DIED]))

ce.add(Comment('''%s says, "%s, you don't look so good!"''', [SPEAKER, JUST_DIED], [SILLY], [RETREATED, DIED]))

ce.add(Comment('''%s says, "%s, you look a little floppy!"''', [SPEAKER, JUST_DIED], [HONEST], [RETREATED, DIED]))

ce.add(Comment('''%s says, "%s, nice choice to run there! A little too late."''', [SPEAKER, JUST_DIED], [SARCASTIC], [RETREATED, DIED]))

ce.add(Comment('''%s slaps %s face. "Hey buddy! You don't look so hot."''', [SPEAKER, JUST_DIED], [UNRELIABLE], [RETREATED, DIED]))

ce.add(Comment('''%s looks at %s. "This is going to be expensive!"''', [SPEAKER, JUST_DIED], [GREEDY], [RETREATED, DIED]))

##############################
## Won

ce.add(Comment('''%s says, "I got the gold!"''', [SPEAKER], [GREEDY], [WON]))

ce.add(Comment('''%s says, "I'm rich!! Well, almost."''', [SPEAKER], [GREEDY], [WON]))

ce.add(Comment('''%s says, "Well fought!"''', [SPEAKER], [BRAVE], [WON]))

ce.add(Comment('''%s claps %s on the shoulder, "I knew I could coun't on you!"''', [SPEAKER, PARTY_MEM], [BRAVE], [WON]))

ce.add(Comment('''%s says, "A fine performance!"''', [SPEAKER], [SERIOUS], [WON]))

ce.add(Comment('''%s says to %s, "Well done."''', [SPEAKER, PARTY_MEM], [SERIOUS], [WON]))

ce.add(Comment('''%s shouts, "Yessss!" and slides into air-guitar.''', [SPEAKER], [SILLY], [WON]))

ce.add(Comment('''%s screams, "Boo-ya!" and high fives %s.''', [SPEAKER, PARTY_MEM], [SILLY], [WON]))

ce.add(Comment('''%s says, "Good job, everyone! Well fought."''', [SPEAKER], [HONEST], [WON]))

ce.add(Comment('''%s says, "That was a tough battle."''', [SPEAKER], [HONEST], [WON]))

ce.add(Comment('''%s says, "I think someone took my share of the gold."''', [SPEAKER], [SNEAKY], [WON]))

ce.add(Comment('''%s says, "I bet there's more stuff around here."''', [SPEAKER], [SNEAKY], [WON]))

ce.add(Comment('''%s claps %s on %s shoulder, "Superior technique, my friend!"''', [SPEAKER, PARTY_MEM, PARTY_MEM_PRONOUN], [CLEVER], [WON]))

ce.add(Comment('''%s claps %s on %s shoulder, "Excellent strategy!"''', [SPEAKER, PARTY_MEM, PARTY_MEM_PRONOUN], [CLEVER], [WON]))

ce.add(Comment('''%s says, "So we won, right?"''', [SPEAKER], [FOOLISH], [WON]))

ce.add(Comment('''%s says, "We could have taken on twice as many %s!"''', [SPEAKER, MON_NAME_PLURAL], [FOOLISH], [WON]))

ce.add(Comment('''%s says, "Those %s didn't scare me!"''', [SPEAKER, MON_NAME_PLURAL], [FOOLISH], [WON]))

ce.add(Comment('''%s says, "Well done, everyone!"''', [SPEAKER], [POLITE], [WON]))

ce.add(Comment('''%s says, "I do hope those %s had life insurance!"''', [SPEAKER, MON_NAME_PLURAL], [POLITE], [WON]))

ce.add(Comment('''%s says, "Bravo! Well fought! Those %s didn't have a chance."''', [SPEAKER, MON_NAME_PLURAL], [POLITE], [WON]))

ce.add(Comment('''%s says, "Those %s were so smart. Not!"''', [SPEAKER, MON_NAME_PLURAL], [SARCASTIC], [WON]))

ce.add(Comment('''%s says, "I almost had to break a sweat."''', [SPEAKER], [SARCASTIC], [WON]))

ce.add(Comment('''%s says, "%s %s? No problem."''', [SPEAKER, MON_COUNT, MON_NAME_PLURAL], [SARCASTIC], [WON]))

ce.add(Comment('''%s looks at %s, "Is everyone ok?"''', [SPEAKER, PARTY_MEM], [LOYAL], [WON]))

ce.add(Comment('''%s says to %s, "We stuck together. Good team work!"''', [SPEAKER, PARTY_MEM], [LOYAL], [WON]))

ce.add(Comment('''%s says, "I could have taken them myself."''', [SPEAKER], [UNRELIABLE], [WON]))

ce.add(Comment('''%s says, "That wasn't so hard."''', [SPEAKER], [UNRELIABLE], [WON]))

ce.add(Comment('''%s says, "%s, I think you deserve a larger share of gold."''', [SPEAKER, PARTY_MEM], [GENEROUS], [WON]))

ce.add(Comment('''%s says, "Wonderful fighting %s! We all deserve a raise!"''', [SPEAKER, PARTY_MEM], [GENEROUS], [WON]))


def comment(sitch, party, room, level):
	try:
		if level.combat_stats.just_died is not None:
			sitch.append(DIED)
	except:
		pass
	sitchv = []
	for s in sitch:
		sitchv.append(SITCH(s))
	env = CommentEnv(party, room, room.monsters, level, sitchv)
	return ce.comment(env, len(sitch))

def get_comment(sitch, party, room, level):
	return comment(sitch, party, room, level)

def print_comment(sitch, party, room, level):
	c = get_comment(sitch, party, room, level)
	if c is not None:
		print c


