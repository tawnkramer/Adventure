import os, sys, time

#this flag will turn on extra diagnostics and functionality to allow for testing.
DEBUG = False

#this flag will turn a level crawler that will try to auto test your level.
CRAWL = False
crawler = None

online = False

input_handler = None

def init_online():
	global online
	#are we online? use command line args to tell
	for arg in sys.argv:
		if arg == 'online':
			online = True

def get_input(prompt):
	if online:
		print '%s' % prompt
		if prompt.find('->') == -1:
			print '->'
		input = raw_input()
	elif input_handler is not None:
		input = input_handler.get_input(prompt)
	else:
		input = raw_input(prompt)
	return input
	
def delete__by_values(lst, values):
    return [ x for x in lst if x not in set(values) ]

def clear_screen():
	if online:
		#this is a platform agnostic symbol to tell clients
		#to clear the screen.
		print '<cls>'
		return
	if CRAWL:
		return
	if os.name == 'posix':
		#we may be on cygwin in windows
		print chr(27) + "[2J"
		return
	os.system('cls' if os.name=='nt' else 'clear')

def pause():
	if online:
		print '->' #to flush io
	
	if CRAWL:
		pass
	elif DEBUG:
		time.sleep(0.1)
	else:
		time.sleep(3)

