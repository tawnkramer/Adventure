from adventure import *
from shop import *
from util import *

#######################################################
# Here is a simple starter level to start learning with. 
# This creates three rooms in a cave and populates with 
# some items and gets it ready for an adventure.
# Read the descriptions and you can guess how it might 
# work. But copy this and use it to start your own! 
# Good luck!!!
#######################################################


#You can make things to discover like this. This makes an Item. The first argument is the name. Keep it short. The second is a description. The third is the location where it's found. Optionally, you can specify how valuable it is. This makes it worth 10 gold pieces.
treasure = Item('bag of gems', 'countless gems and jewels', 'scattered around the room.', GP(10))

#Sometimes it's fun to make items that don't have much use, but make us laugh!
fries = Item('bag of fries', 'old, old, moldy, disgusting but somewhat tempting french fries', 'on the wet, soggy ground behind some rocks.')

#You can make monsters like this. You can also use the master list of pre-created monsters with the function Mon which takes a monster name as an argument.
#This Dragon has two attacks. The first part of the attack is what it looks like when it's used. The second is the max damage.
dragon = Monster('Dragon', "On top of the coins sits the largest red dragon you've ever seen!", 60, [ MonsterAttack('clawed', 7), MonsterAttack('spewed flames', 9) ], 300 )

#sometimes it's fun to connect rooms with a door and then hide the key. A key is a special item because of it's name. 
#Keep it 'key' until you know how to match it with doors specifically.
key = Item('key', 'a large silver dragon key', 'hidden in the pot under lots of spider webs.')
door = Door("a strong door with a silver dragon crest around the key hole.")

#Here's how to make some rooms. These can be indoor or outdoor spaces. Use your imagination to create a cool environment.
#The first argument is the name. 
#The second, optional argument, is the description you see only when you first enter a room.
#The third argument is what you see every time after the first entry. 
#The fourth argument finishes the sentence "[Direction] you see" in order to give the party some indication of what can be seen from the current space.
#The fifth optional argument is the list of items you will find if you search.
#The sixth argument is the list of monsters in the room.
cave = Room( "Cave", None, "This large cave has the smell of wet dirt and old grease." , 
				"a glimmer of light shines through the distant cave entrance.", [fries]  )
small_tunnel = Room("Small Tunnel", None, "Down the small tunnel you see a small golden pot. The tunnel stops here.", "a small tunnel.", [key])
dragon_room = Room("Dragon's Lair", None, "There is a huge pile of coins in the center of a large cave.", "a pile of coins.", [treasure], [dragon])

#If you want to make a fun ascii banner, like the Ragged Keep, check out
#http://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20
#then pass it as the optional second argument to Level

#You need to make one level
level1 = Level ("The Cave of Fear")

#connect your rooms together like this. The door is optional.
cave.connect("East", dragon_room, door)
cave.connect("West", small_tunnel)

#and start the level like this, passing the level an the first room to begin.
run_adventure(level1, cave)

