from adventure import *
from shop import *
from util import *


#You can make things to discover like this. This makes an Item. The first argument is the name. Keep it short. The second is a description. The third is the location where it's found. Optionally, you can specify how valuable it is. This makes it worth 10 gold pieces.
treasure = Item('bag of gems', 'countless gems and jewels', 'scattered around the room.', GP(10))

#Sometimes it's fun to make items that don't have much use, but make us laugh!
fries = Item('bag of fries', 'old, old, moldy, disgusting but somewhat tempting french fries', 'on the wet, soggy ground behind some rocks.')
old_bones = Item('old bones', 'a pile of old bones, probably from a cat', 'hidden in the rags.', GP(1))
golden_skull = Item('golden skull', 'a wicked looking gold skull', 'hidden among the spider webs. It looks quite valuable.', GP(20))

#You can make monsters like this. You can also use the master list of pre-created monsters with the function Mon which takes a monster name as an argument.
#This Dragon has two attacks. The first part of the attack is what it looks like when it's used. The second is the max damage.
dragon = Monster('Dragon', "On top of the coins sits the largest red dragon you've ever seen!", 60, [ MonsterAttack('clawed', 7), MonsterAttack('spewed flames', 9) ], 300 )

#sometimes it's fun to connect rooms with a door and then hide the key. A key is a special item because of it's name. 
#Keep it 'key' until you know how to match it with doors specifically.
silver_key = Item('key', 'a large silver dragon key', 'hidden in the pot under lots of spider webs.')
wood_door = Door("a strong door with a silver dragon crest around the key hole.", silver_key)

#Here's how to make some rooms. These can be indoor or outdoor spaces. Use your imagination to create a cool environment.
#The first argument is the name. 
#The second, optional argument, is the description you see only when you first enter a room.
#The third argument is what you see every time after the first entry. 
#The fourth argument finishes the sentence "[Direction] you see" in order to give the party some indication of what can be seen from the current space.
#The fifth optional argument is the list of items you will find if you search.
#The sixth argument is the list of monsters in the room.
cave = Room( "Cave", None, "This large cave has the smell of wet dirt and old grease." , 
				"a glimmer of light shines through the distant cave entrance.", [], [  ] )
				
small_tunnel = Room("Small Tunnel", None, "Down the small tunnel you see a small golden pot. The tunnel stops here.", "a small tunnel.", [silver_key], [Mon('Orc'), Mon('Orc'), Mon('Orc')] )

empty_room = Room("Empty stone room", None, "An empty looking room.", "an empty looking room.", [golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull, golden_skull],[ Mon('Orc'),  Mon('Orc'),  Mon('Orc'),  Mon('Orc'),  Mon('Orc')])

split_tunnel = Room("split tunnel", None, "This tunnel splits in four direction", "tunnels that split", [old_bones, old_bones, golden_skull])

old_shack = ShopRoom( "old shack", '''Theres an VERY old lady sleeping in a corner of a shack.She wakes with a start at the sound of your feet. 
"oh! its another humen!Thanks for saveing me! but no point going out with no money. would you like to buy something?"''',
'''Welcome back! care to buy anything?
''', 'old shop.', all_items + [] )

#If you want to make a fun ascii banner, like the Ragged Keep, check out
#http://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20
#then pass it as the optional second argument to Level

#You need to make one level
level1 = Level ("The Cave of Fear")

#connect your together like this. The door is optional.
cave.connect("East", split_tunnel)
cave.connect("West", small_tunnel)
small_tunnel.connect("North", old_shack, wood_door)
split_tunnel.connect("South", empty_room)


#and start the level like this, passing the level an the first room to begin.
run_adventure(level1, cave)

