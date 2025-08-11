A simple Python script to scrape .jar games from dedomil.net.
This script only downloads games for 240x320 screens, which is the id "8" in dedomil's database.

# How to use:
1. First, use `python run.py` to scrape games, the games' IDs are from 1 -> 8483 (as of 11 Aug 2025)
2. If any game failed to download, run `python run.py --retry`, then enter the path of the newest log file to try again failed games.
3. Then use `python rename.py` to rename the downloaded .jar files according to their names and vendors, declared in each .jar file's META-INF
4. Some of the games on dedomil.net are in Czech. If you don't want those, then run `python runcz.py` using the same range of IDs to download English versions of games that have both Czech and English versions.

# Note:
- Games are saved to /jar. Modify the source code if you want to use another folder.
- Total number of games on dedomil.net at the moment:8483
- URL used for downloading game: http://dedomil.net/games/<game_id>/screen/<screen_id>
- dedomil's screen ids:
	+ 128x128 = 2
	+ 128x160 = 3
	+ 176x208 = 4
	+ ???x??? = 5
	+ 176x220 = 6
	+ 208x208 = 7
	+ 240x320 = 8
	+ 240x400 = 9
	+ 240x432 = 10
	+ 320x240 = 11
	+ ???x??? = 12
	+ 320x480 = 13
	+ 352x416 = 14
	+ 360x640 = 15
	+ ???x??? = 16
	+ 480x800 = 17