The code in this folder is designed as a simple predictive text program. 

fanfictionscraper.py and lyricscraper.py analyze text for word frequency and save the data into a file

predictive text.py reads those files and generates sentences based on them.

This folder comes preloaded with some data created by fanfictionscraper.py and lyricscraper.py for use on testing predictive text.py

fanfictionscraper.py reads through stories from fanfiction.net from oldest to newest and analyzes word frequencies and distributions. It creates the defaultFanficDataFile and postCountFordefaultFanficDataFile files and is best run in the background to passively collect lots of data without requiring user input. defaultFanficDataFile is formatted for use by predictive text.py, while postCountFordefaultFanficDataFile is only used in fanfictionscraper.py

lyricscraper.py interacts with the lyric files created by the lyric analyzer code. When given input artists or list of songs, it analyzes word frequencies and saves them in a file named DataFor[ARTIST]With[X]MoreAt[TIMESTAMP], which is compatible with predictive text.py. It does not save new lyrics or artists, but instead only uses what is local on the machine. It can read artists and songs from a webpage, however. This code is the most recent and was designed to use some resources from a seperate project in this

predictive text.py uses a simple algorithm to create 20 sentences from the data produced by the other programs. It allows the user to select a data file to use and then creates sentences. Potentially, the user could create a program that pulls text and analyzes it from another source and, as long as the data is saved in a compatible manner, use this code to create sentences. The sentence creation algorithm is not ideal, so this is very much a work in progress. It is entertaining to me, to say the least. I used similar code to analyze group messages in the messaging app GroupMe and create sentences that my friends would say. The sentences rarely make sense semantically, but we all enjoy it.