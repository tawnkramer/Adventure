from adventure import *
from prettytable import *
from stuff import *
import time
import copy
import os
from util import *

everything = all_weapons + all_spells + all_items + all_armor

class Shop(object):
	def __init__(self, name=None, desc=None):
		self.name = name
		self.description = desc
		self.inventory = []
		self.list = []
		self.player = None
		self.show = None
		self.unsaved_changes = False
		
	def add_item(self, item):
		self.inventory.append(item)
		
	def add_items(self, items):
		for i in items:
			self.add_item(i)
			
	def enter_shop(self, p):
		self.player = p
		if self.name is None:
			return
		print '\n\n--------------------------------------------'
		print ' ', self.name
		print
		print self.description
		print
		
	def show_items(self):
		if self.show is None:
			return
		
		self.list = []
		for item in self.inventory:
			if self.show == 'all':
				self.list.append(item)
			elif self.show == 'weapons' and item.is_weapon():
				self.list.append(item)
			elif self.show == 'armor' and item.is_armor():
				self.list.append(item)
			elif self.show == 'spells' and item.is_spell() and not item.is_healer_cat():
				self.list.append(item)
			elif self.show == 'healing' and item.is_spell() and item.is_healer_cat():
				self.list.append(item)
			elif self.show == 'items' and not item.is_spell() and not item.is_armor() and not item.is_weapon():
				self.list.append(item)
				
		if self.show == 'magic_items':
			self.list = magic_items
			
		count = len(self.list)
		i = 0
		print '\nItems:\n'
		header = ['sel', 'name', 'cost', 'description']
		if self.show == 'spells' or self.show == 'healing':
			header.append('mana')
			header.append('damage')
		elif self.show == 'weapons':
			header.append('damage')
			
		t = PrettyTable(header)
		show_mark_help = False
		while i < count:
			item = self.list[i]
			i = i + 1
			mark = ''
			if not self.player.has_skill(item.cat):
				mark = '*'
				show_mark_help = True
			if item.is_spell():
				t.add_row( [i, '%s%s' % (item.name, mark), item.cost.get_str(), item.description, item.mana, item.damage] )
			elif item.is_weapon() and not item.is_magic():
				t.add_row( [i, '%s%s' % (item.name, mark), item.cost.get_str(), item.description, item.damage] )
			else:
				t.add_row( [i, '%s%s' % (item.name, mark), item.cost.get_str(), item.description] )
		result = t.get_string(hrules=HEADER)
		print result
		if show_mark_help:
			print '* : requires additional training.'
		self.show_player_gp()
		print
		
	def make_purchase(self, sel):
		global DEBUG
		if sel < 0 or sel >= len(self.list):
			print 'Selection was not valid.'
			return False
		item = self.list[sel]
		count = 1
		if item.is_food() or item.is_drink():
			cstr = get_input('This item can be purchased in quanty. How many would you like? -> ')
			count = int(cstr)			 
		if self.player.gp < item.cost.count * count and not DEBUG:
			print 'The player does not have enough money for this purchase'
			pause()
			return False
		if not self.player.has_skill(item.cat):
			print 'The player does not have the training to use this item. Skill required:', get_skill_str(item.cat)
			yn = get_input('Would you like to buy anyway? (y, n) -> ')
			if yn == 'n':
				return False
		yn = get_input('Are you sure %s wants to purchase %d %s for %d gold? (y, n) -> ' %(self.player.name, count, item.name, item.cost.count * count))
		if yn != 'y':
			return False
		self.player.gp -= (item.cost.count * count)
		for i in range(0, count):
			self.player.add(copy.deepcopy(item))
		if item.is_weapon() or item.is_armor():
			self.player.activate(item)
		self.unsaved_changes = True
		if count > 1:
			print self.player.name, 'has purchased', count, item.name, 'for', item.cost.count * count, 'gp.'
		else:
			print self.player.name, 'has purchased', item.name, 'for %s.' % item.cost.get_str()
		print self.player.name, 'has', self.player.gp, 'gp remaining.'
		return True
		
	def show_player_items(self):
		print self.player.name, 'Items:'
		self.player.show_inventory()
		print 'gp: ', self.player.gp

	def show_player_gp(self):
		print self.player.name, 'gp:', self.player.gp
		
	def sell(self):
		clear_screen()
		print self.player.name, 'Items:'
		t = PrettyTable(['sel', 'name', 'sell price'])
		i = 1
		#sell things for a fraction the original cost
		#this is random to represent the different buyers offers
		fc = random.randint(50, 95)
		fc = float(fc) / 100.0
		to_sell = []
		for item in self.player.inventory:
			if item.cost is None:
				item.cost = GP(1)
			cost = int(item.cost.count * fc)
			if cost == 0 or item.is_spell():
				continue
			to_sell.append(item)
			t.add_row([i, item.name, cost])
			i = i + 1
		print t.get_string(hrules=ALL)
		print
		sel = get_input("Enter the sel of the item to sell, 0 for cancel -> ")
		try:
			iSel = int(sel) - 1
			if iSel >= 0 and iSel < len(to_sell):
				item = to_sell[iSel]
				if item.is_spell():
					print "Spells can't be sold or given away. They are embeded in your spell book."
					return
				yn = get_input( "Are you sure %s wants to sell %s for %d gold? (y, n) -> " % (self.player.name, item.name, int(item.cost.count * fc) ) )
				if yn == 'y':
					self.player.gp += int(item.cost.count * fc)
					self.player.remove(item.name)
					print item.name, 'is sold.'
		except:
			print 'input not a number.'
	
	def print_menu(self):
		if self.show is None:
			print '\nLook at:\n w-weapons\n m-magic\n h-healing\n a-armor\n e-equipment\n g-magic items\n i-show your items\n s-sell\n l-leave'
		else:
			print 'Enter item sel number to purchase\n i-show your items\n s-sell\n b-back\n l-leave'
		
	def get_command(self):
		com = get_input("\nEnter command -> ")
		return com
		
	def do_shop(self):
		done = False
		while not done:
			self.show_items()
			self.print_menu()
			com = self.get_command()
			iSel = 0
			try:
				iSel = int(com)				
			except:
				pass
				
			if iSel != 0:
				self.make_purchase(iSel - 1)
				
			if com == 'l':
				done = True
			if com == 'b':
				self.show = None
			elif com == 'w':
				self.show = 'weapons'
			elif com == 'm':
				self.show = 'spells'
			elif com == 'h':
				self.show = 'healing'
			elif com == 'a':
				self.show = 'armor'
			elif com == 'e':
				self.show = 'items'
			elif com == 'g':
				self.show = 'magic_items'
			elif com == 'i':
				self.show_player_items()
			elif com == 's':
				self.sell()

new_inventory = None

def set_new_shop_inventory(inven):
	global new_inventory
	new_inventory = inven

class ShopRoom(Room):
	def __init__(self, name, initial_description, description, distant_view, inventory):
		super(ShopRoom, self).__init__(name, initial_description, description, distant_view )
		self.shop = Shop()
		self.shop.add_items(inventory)
		
	def on_enter(self, party, level, entered_from_room=None):
		global new_inventory
		if new_inventory is not None:
			self.shop.inventory = []
			self.shop.add_items(everything)
		super(ShopRoom, self).on_enter(party, entered_from_room )
		
	def update(self, party, level):
		done = False
		while not done:
			if len(party) == 1:
				user = party[0]
			else:
				print 'Select player to shop'
				user = self.choose_player(party)
				if user is None:
					done = True
			if user is not None:
				if user.is_trapped():
					print user.name, "can't shop.", user.get_trapped_desc()
				elif not user.is_alive():
					print user.name, "can't shop. He is barely conscious."
				else:
					self.shop.enter_shop(user)
					while self.shop.do_shop():
						pass
			if len(party) == 1:
				done = True
			else:
				yn = get_input("Does anyone else want to shop? (y, n) -> ")
				if yn == 'n':
					done = True
		print 'Leaving %s.' % self.name
		pause()
		return self.choose_room_to_run()
	
	