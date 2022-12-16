from items import Item

class Potion(Item):

	def is_potion(self):
		return True
	
	def drink(self, drinker):
		pass
		
		
class InvisibilityPotion(Potion):

	def drink(self, drinker):
		drinker.hidden = True
		print('%s suddenly disappears completely.' % drinker.name)

class HealingPotion(Potion):

	def drink(self, drinker):
		if drinker.is_alive():
			drinker.fully_healed()
			print('%s is fully healed!' % drinker.name)
		
	
