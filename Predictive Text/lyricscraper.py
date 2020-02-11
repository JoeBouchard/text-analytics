import time, sys, os, re, math, string, requests, tkinter
from tkinter.filedialog import askopenfilename

##Establish a list of punctuation
pun=string.punctuation
pun=pun.replace("'", '')

##Get the location of the music data to use
tkinter.Tk().withdraw()
musicDir = askopenfilename(title="Select the lyric analysis.py file at the root of the music data you want to use")
while '\\' in musicDir:
    musicDir = musicDir.replace('\\', '/')
musicDir = musicDir.replace('/lyric analysis.py', '')

##Create a method to find artists on a given webpage
def artistFinder(url='https://www.billboard.com/charts/country-songs'):
    toReturn = []

    ##Open the passed in webpage and get raw text
    x=requests.get(url)
    bigData=x.text
    x.close()

    ##Format it for easier parsing
    bigData=bigData.lower()
    remChar = ['!', '.', '+ ', '\'', '/']
    for ch in remChar:
        bigData = bigData.replace(ch, '')

    ##Read in lists of valid and invalid artists
    art = open(musicDir+'/Metadata/validArtists.txt')
    validArtists = eval(art.read())
    art.close()

    art2 = open(musicDir+'/Metadata/badArtistList.txt')
    badList = eval(art2.read())
    art2.close()

    ##Iterate through each artist and try to find it on the page
    print('searching for artists alphabetically')
    for artist in validArtists:
            if (artist.replace("-", " ") in bigData.lower() and artist not in badList):
                ##Add valid artists to the list and print that they were found
                toReturn.append(artist)
                print(artist)

    ##Return the list of found artists
    return toReturn

##Find songs on a webpage. More efficient with wikipedia and billboard.com
def songFinder(url='https://www.billboard.com/charts/country-songs'):

    ##Establish list to hold filename of all songs found
    toReturn = []

    ##Get the webpage and raw text on it
    x=requests.get(url)
    bigData=str(x.text)
    x.close()

    ##Format the text for easier parsing
    bigData=bigData.lower()
    remChar = ['!', '.', '+ ', '\'',]
    for ch in remChar:
        bigData = bigData.replace(ch, '')

    ##Search more specifically for wikipedia if the page is on wikipedia
    ##Potentially could find new songs and artists this way
    if('wikipedia' in url):

        ##Format specifically for wikipedia
        bigData = bigData.replace('_', '-')
        bigData = bigData.lower()
        bigD = bigData.split('/wiki/')

        ##Establish a variable to hold only song titles
        allSongs = []

        ##Reformat local song titles to match wikipedia's formatting
        for file in os.listdir(musicDir+"/lyrics"):
            try:
                allSongs.append(file[0:file.find('-lyrics-')])
            except:
                print("Invalid :"+file)

        ##Search through the wikipedia chunks to find songs. Song titles will always be listed first. 
        for i in bigD:
            if i[0:i.find('"')] in allSongs and i[0:i.find('"')] not in toReturn:
                ##Display songs found and add them to the list
                print(i[0:i.find('"')])
                toReturn.append(i[0:i.find('"')])

    ##Search specifically through the Billboard top 100s site
    ##Potentially could find new songs and artists with this
    elif('billboard' in url):

        ##Format for Billboard
        bigData = bigData.replace(' ', '-')
        bigData = bigData.lower()
        bigD = bigData.split('item-details__title">')

        ##Create a list of only song titles
        allSongs = []
        for file in os.listdir(musicDir+"/lyrics"):
            try:
                allSongs.append(file[0:file.find('-lyrics-')])
            except:
                print("Invalid :"+file)

        ##Find song titles on Billboard page
        for i in bigD:
            if i[0:i.find('</div')] in allSongs and i[0:i.find('</div')] not in toReturn:
                print(i[0:i.find('</div')])
                toReturn.append(i[0:i.find('</div')])
        
    ##Generic search for all other sites
    else:

        ##Read in all valid songs
        allSongs = []
        f=open(musicDir+"/Metadata/validSongsList.txt")
        allSongs = eval(f.read())
        f.close()

        ##Search on page for songs
        print('searching for songs alphabetically')
        for song in allSongs:
                if (len(song) > 3 and song.replace("-", " ") in bigData.lower()):
                    ##Add valid songs to the list and display them
                    toReturn.append(song)
                    print(song)
                if(allSongs.index(song)%3000 == 0):
                    print(allSongs.index(song))

    ##Return a list of found songs
    return toReturn

##Method to search through local songs by artists in a list
def finderByArtist(artists=['Taylor Swift']):

    ##Establish list to hold lyrics    
    lyrics = []

    ##Read in list of all songs
    allSongs = []
    for file in os.listdir(musicDir+"/lyrics"):
        allSongs.append(file)
    
    ##Create and format the list of artists to search for
    artistsToFind = []
    if len(artists) > 0:
        for i in artists:
            i=i.lower()
            artistsToFind.append(i.replace(' ', '-'))

        counter = 0
        ##Begin search loop
        for j in allSongs:
            ##Check every given artist
            for k in artistsToFind:
                ##If the artist is in the song title
                if 'lyrics-'+k+'.txt' in j:
                    ##Open the file containing the song lyrics, if possible
                    try:
                        l=open(musicDir+'/lyrics/'+j)
                        data=l.read()
                        l.close()
                    except:
                        data = ''

                    ##Pretty much all English songs will have the word 'the' in them
                    ##Check to confirm the song is valid
                    if 'the' in data:
                        ##Add lyrics of the valid song to the list of lyrics 
                        counter+=1
                        lyrics.append(data)
                        if(counter%20 == 0):
                            print(counter)
                    else:
                        print('Found invalid song: \t'+j)
                            
    ##If list is empty, search all artists and songs
    else:
        art = open(musicDir+'/Metadata/validArtists.txt')
        artistsToFind = eval(art.read())
        art.close()
        print('Evaluating all '+str(len(artistsToFind))+' artists')
        

        ##Start the searching loop iterating through all songs
        counter = 0
        for j in allSongs:
            try:
                l=open(musicDir+'/lyrics/'+j)
                data=l.read()
                l.close()
            except:
                data = ''

            ##Pretty much all English songs will have the word 'the' in them
            ##Check to confirm the song is valid
            if 'the' in data:
                ##Add lyrics of the valid song to the list of lyrics 
                counter+=1
                lyrics.append(data)
                if(counter%20 == 0):
                    print(counter)
            else:
                print('Found invalid song: \t'+j)
                
    ##Return a list containing song lyrics  
    return lyrics

##Find specific songs given in a passed in list
def finderBySong(songs=['ours']):

    ##Establish a list to hold all the lyrics
    lyrics = []

    ##Get all the songs on this local machine
    allSongs = []
    for file in os.listdir(musicDir+"/lyrics"):
        allSongs.append(file)

    ##Format the list of songs to be compatible with the local filenames
    songsToFind = []
    if len(songs) > 0:
        for i in songs:
            i=i.lower()
            songsToFind.append(i.replace(' ', '-'))
    ##If no songs were specified, search through all
    else:
        songsToFind = []
        
    ##Begin search loop
    numFound = 0
    songsToFind.sort()
    for k in songsToFind:
        ##Remove artist from song title
        songTitle = k.split('-lyrics')[0]

        found = False

        ##Iterate through all songs to find one with a matching title
        for j in allSongs:

            ##Check if the current song in iteration is the one we're looking for
            if songTitle+'-lyrics-' == j[0:len(songTitle)+8]:

                if(numFound % 20 == 1):
                    print(numFound)

                ##Attempt to read the lyrics from a file
                try:
                    l=open(musicDir+'/lyrics/'+j)
                    data=l.read()
                    l.close()
                except:
                    data = ''

                ##Confirm the lyrics are valid and not a repeat
                if 'the' in data and '-version-' not in j:
                    ##Add to the list of lyrics and increment the counter
                    lyrics.append(data)
                    numFound+=1
                    found = True
                    break
                else:
                    print('Found invalid song: \t'+j)

                    found = False
                    break

        ##Remove songs that have been found from the large list of songs
        if found:
            allSongs.remove(j)
                
    ##Return a list of lyrics
    return lyrics

##Get the contextual data from a list of lyrics
def textScraper(lyrics):

    ##Establish a dictionary to hold the context data
    toReturn = {'START':{}, '.':0}

    ##Loop through all songs in the list
    for m in lyrics:

        ##Print the counter occasionally
        if lyrics.index(m)%100 == 0:
            print(lyrics.index(m))

        ##Split the lyrics into sentences
        sentences=re.split('\. |\? |! |\n |- ', m.lower())

        ##Iterate through all sentences
        for i in sentences:
            thisSentence=i
            ##Replace all punctuation and newlines with spaces
            for j in pun:
                while j in thisSentence:
                    thisSentence=thisSentence.replace(j, ' ')
            while '\n' in thisSentence:
                thisSentence=thisSentence.replace('\n', ' ')

            ##Split the sentence down to its words and remove the empty string
            words=thisSentence.encode('ascii', 'ignore').decode('ascii').split(' ')
            while '' in words:
                words.remove('')

            ##Iterate through the words
            for count in range(0, len(words)):

                ##Remove all special characters from the words
                w=words[count].encode('ascii', 'ignore').decode('ascii')
                ##Check to see if the word is valid
                if w.isprintable and w != '':

                    ##Add the word to the dictionary if the word is new
                    if w not in list(toReturn.keys()):
                        toReturn[w] = {'.':0}

                    ##If the word starts the sentence, deal with it accordingly
                    if count == 0:

                        ##Add word to the list of first words, if it's new
                        if w not in list(toReturn['START'].keys()):
                            toReturn['START'][w] = 0

                        ##Add following word to the dictionary if it's new
                        if len(words) >= 2 and words[count+1] not in list(toReturn[w].keys()):
                                toReturn[w][words[count+1]] = 0

                        ##Increment context data counters
                        toReturn['START'][w]+=1
                        if len(words) >= 2:
                            toReturn[w][words[count+1]]+=1
                        else:
                            toReturn[w]['.'] += 1
                    else:
                        ##If the word ends the sentence
                        if count+1 == len(words):
                            ##If it's never ended a sentence before, add the '.' value
                            if '.' not in list(toReturn[w].keys()):
                                toReturn[w]['.']=0
                            ##Increment the '.' value
                            toReturn[w]['.']+=1
                        else:
                            ##If the word is in the middle of the sentence
                            ##If the word is followed by a new word, make space for it
                            if words[count+1] not in list(toReturn[w].keys()):
                                toReturn[w][words[count+1]] = 0
                            ##Increment context data counter 
                            toReturn[w][words[count+1]]+=1
            ##Increment average sentence counter in dictionary
            toReturn['.']+=1
    ##Divide total sentences by number of songs to get the average song length in sentences
    toReturn['.'] = toReturn['.']/len(lyrics)

    ##Return the data
    return toReturn

print('''Welcome to the data aggregator for song lyrics.
The functionality of this code is limited to the number of songs collected by
lyric analyzer.py, which came bundled with this. This code cannot analyze songs
or artists that have not first been analyzed by lyric analyzer.py.''')

##Read in user's initial information
intake=input("Would you like to get data based on artists [a] or songs [s]\n")
listOfSongs = []
listOfArtists = []

##Take action if the user wants to sort by artist or gives any input other than song
if (intake.lower()[0] != 's'):
    stringOfArtists=input("Give the artists you would like to search for in a comma-seperated list or the URL of a website to search through\n")
    ##Search a website if a URL is given
    if(('/' or '\\') and '.' in stringOfArtists and ', ' not in stringOfArtists):
        listOfArtists = artistFinder(stringOfArtists)
    ##Create a list if a list is given
    else:
        listOfArtists = stringOfArtists.split(', ')

    ##Establish a list of lyrics to parse
    thisData = finderByArtist(artists=listOfArtists)

##Take action if the user wants to sort by song
else:
    stringOfSongs=input("Give the songs you would like to search for in a comma-seperated list or the URL of a website to search through\n")
    ##Search a website if a URL is given
    if(('/' or '\\') and '.' in stringOfSongs and ', ' not in stringOfSongs):
        listOfSongs = songFinder(stringOfSongs)
    ##Create a list if a list is given
    else:
        listOfSongs = stringOfSongs.split(', ')

    ##Establish a list of lyrics to parse
    thisData = finderBySong(songs=listOfSongs)

##Parse the data
parsedData = textScraper(thisData)
##Save the data
file = open('DataFor'+max(listOfSongs, listOfArtists)[0]+'With'+str(len(max(listOfSongs, listOfArtists))-1)+'MoreAt'+str(int(time.time())), 'w')
file.write(str(parsedData))
file.close()
print("Your data has been saved to\n\nDataFor"+max(listOfSongs, listOfArtists)[0]+'With'+str(len(max(listOfSongs, listOfArtists))-1)+'MoreAt'+str(int(time.time())))
print("\nin this directory. It can now be used by predictive text.py")


