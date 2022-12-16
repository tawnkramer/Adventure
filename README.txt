README.txt
Author : Tawn Kramer
Date: Jan 25, 2014

   _____       .___                    __                         ._.
  /  _  \    __| _/__  __ ____   _____/  |_ __ _________   ____   | |
 /  /_\  \  / __ |\  \/ // __ \ /    \   __\  |  \_  __ \_/ __ \  | |
/    |    \/ /_/ | \   /\  ___/|   |  \  | |  |  /|  | \/\  ___/   \|
\____|__  /\____ |  \_/  \___  >___|  /__| |____/ |__|    \___  >  __
        \/      \/           \/     \/                        \/   \/

This is a text based dungeon crawl engine in python. A few dungeons are included. Feel free to make your own!


1. What is a text based adventure?

Well, back in the old days, before fancy graphics, the first games were made as a kind of interactive story. In this case, text is printed out giving you a description of things you see and giving you ideas about what you can do. You get to type one of the many commands and then hit enter and see what happens.



2. How do I start?

If you have wxPython installed, you can try python win_client.py. If you need wxPython this command might install it "python -m pip install wxpython".

Otherwise, you can start by typing python TheRaggedKeep.py. This will start you out. It helps if you can resize your terminal window, as some text tables require extra width. On Windows DOS environments, you may probably want to try the win_client.py instead.


3. Can I make my own levels?

I'm so glad you asked! :-)
I've made a simple level, called SimpleLevel.py. Try opening that up and taking a look. You can run it by typing python SimpleLevel.py. First make a copy of the level. You can type cp SimpleLevel.py MyLevel.py and that will make a copy for you. Then open a text editor and try making changes. 

Check out TheRaggedKeep.py for ideas about how to make things more complicated.

And be sure to share your levels with your friends! Everyone likes a good adventure.



4. How can I play with my friends?

Well, if your friends are far away, you can try to setup a network game. In this mode, everyone connects to a server and then you all see the same game at once. Anyone can type commands. And you all can chat. It takes a little network knowledge to setup the server. So try googling "setup port forwarding" and then forward port 9999 to your computer.

Run a server by typing python server.py

You can connect to the server on the command line with python client.py server=your_server_ip name=yourname

your_server_ip is something like www.foo.com or 192.168.0.32. Type ipconfig on a windows machine or ifconfig on a linux like machine to see your servers ip address. If you are behind a router, you will have the use the router ip address.



5. Do I have to play in a terminal?

If you want to try the windows client, you can make sure you have wxPython installed and then run python win_client.py. This can run a local game as well as connect to server games.



6. I don't like the rules!

Well, then change them :-) You have all the source files to adjust the rules so they make sense to you. Try taking a look at adventure.py, combat.py and others to see how things work. When making changes, try running the extra command argument DEBUG, like python TheRaggedKeep.py DEBUG. This puts the game in a special mode where you can get more feed back when things crash. You can also have super powers to jump to any room and defeat monsters easily to test your level.

