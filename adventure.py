import combat
import pickle
import random
import time
import copy
import os
import player_editor
from prettytable import *
import util
from commentary import *
from stuff import *
from monsters import *
from potions import *
from scrolls import *
from room import *
from player import Player
from level import Level
from crawler import Crawler
		
def gather_party(level):
	if util.CRAWL:
		level.difficulty = 1
		return [util.crawler]
	print("\nPlease enter the name of a player which will start this adventure. You may use your real name, but it can be fun to make up new one.")
	done = False
	party = []
	p = Player('loader')
	while not done:
		who = util.get_input("Enter player name ( f-finished ) -> ")
		if who == 'f' or len(who) < 1:
			done = True
		else:
			valid = True
			for p in party:
				if who == p.name:
					print("Sorry, each player can be in the party only ONCE!")
					valid = False
			if not valid:
				continue
			np = p.load(who)
			if np is None:
				print(who, 'looks like a new player. Welcome %s!' % who)
				yn = util.get_input('Shall we create %s now? (y, n) -> ' % who)
				if yn == 'y':
					np = Player(who)
					player_ready = False
					while not player_ready:
						util.clear_screen()
						ed = player_editor.PlayerEditor(all_skills)
						ed.do_edit(np)
						util.clear_screen()
						if np.gp == 0:
							print("You don't have any gold. Are you sure you rolled for attributes (r)?")
							util.get_input('Hit return to go back to player editor.')
						elif np.sp == 4:
							print("You must choose some area of training. Use your skill points or you can't purchase items for combat.")
							util.get_input('Hit return to go back to player editor.')
						else:
							player_ready = True
					print('Looking very good %s! Welcome to the party.' % np.name)
					party.append(np)
					print('Will somone else be joining us?')
				else:
					print("OK. I was hoping you would say yes. You can't join in the fun without creating a player. Just hit the y key and then enter next time.")
			else:
				if np.is_alive():
					np.fully_healed()
				np.on_combat_end()
				party.append(np)
	print("Ok, the party has gathered!")
	level.set_difficulty()
	print("Excellent!! And so we shall begin...")
	util.pause()
	return party
	
def handle_commandline_options():
	#setup online interactions
	util.init_online()
	
	for arg in sys.argv:
		if arg.upper() == 'DEBUG':
			util.DEBUG = True
		elif arg.upper() == 'CRAWL':
			util.CRAWL = True
			util.DEBUG = True
			
	if util.CRAWL == True:
		util.crawler = Crawler()
	
def show_dd():
	print('''
   _____       .___                    __                        
  /  _  \    __| _/__  __ ____   _____/  |_ __ _________   ____  
 /  /_\  \  / __ |\  \/ // __ \ /    \   __\  |  \_  __ \_/ __ \ 
/    |    \/ /_/ | \   /\  ___/|   |  \  | |  |  /|  | \/\  ___/ 
\____|__  /\____ |  \_/  \___  >___|  /__| |____/ |__|    \___  >
        \/      \/           \/     \/                        \/
	''')
	
	
def run_adventure(level1, home):
	party = []
	
	#setup command line options
	handle_commandline_options()
	
	#should we load a game in progress?
	util.clear_screen()
	show_dd()
	yn = util.get_input("Welcome to a text based adventure similar too, but not exactly like, other ttrpgs!!\nAre you starting a new game? (y, n) -> ")
	loaded_level = None
	
	#attempt to load the saved level
	if yn == 'n':
		loaded_level = level1.load(party)
	else:
		party = gather_party(level1)
	
	if len(party) == 0:
		print("Can't continue with an empty party.")
		return
	
	#either start the level or assign the loaded level	
	if loaded_level is not None:
		#add any missing rooms since we saved.
		loaded_level.add_missing_rooms(home)
		loaded_level.scale_difficulty(party)
		level1 = loaded_level
		util.pause()
		util.clear_screen()
		level1.current_room.on_enter(party, level1)
	else:
		level1.start(home, party)
	
	if util.DEBUG:
		#in debug mode, we want to see the traceback!
		while level1.update(party):
			pass
		return
	
	#in release mode, we want to have this catch-all to
	#handle crashes.
	keep_going = True
	while keep_going:
		try:
			keep_going = level1.update(party)
		except:
			print('-------------------------------------')
			print('Sorry, the adventure crashed!')
			print('The game will keep going, but you might want to revert to an earlier save file.')
			print('-------------------------------------')
			print()


if __name__ == "__main__":
	print("This is not meant as the starting point. Try running 'python TheRaggedKeep.py'")
