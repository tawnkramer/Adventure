import adventure
import player_editor
import sys

name = None
if len(sys.argv) != 2:
	name = input('please enter the player name -> ')
else:
	name = sys.argv[1]

p = adventure.Player('t')
t = p.load(name)
t.skills = []
t.sp = 4
ed = player_editor.PlayerEditor(adventure.all_skills)
ed.do_edit(t)

