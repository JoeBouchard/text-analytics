import os, sys, time, urllib3, certifi

##Establish the working directory
workingDir = "/".join(sys.path[0].split("\\")[0:-1])+"/"
print(sys.path[0])
print(workingDir)

##Check if directory is structured correctly
contents = os.listdir()
if ("Metadata" not in contents or "lyrics" not in contents):
    os.system("mkdir Metadata")
    os.system("mkdir lyrics")
    os.system('mkdir "Data By Key"')

##Open saved lists of validated and invalidated songs and artists
try:
    x = open("Metadata/validSongsList.txt")
    totalValid = eval(x.read())
    x.close()
    totalValid.sort()
except FileNotFoundError:
    totalValid = []
    
try:
    x = open("Metadata/validArtists.txt")
    validArtists = eval(x.read())
    x.close()
except FileNotFoundError:
    validArtists = []

try:
    x = open("Metadata/invalidArtists.txt")
    invalidArtists = eval(x.read())
    x.close()
except:
    invalidArtists = []

try:
    x = open("Metadata/badArtistList.txt")
    badList = eval(x.read())
    x.close()
except:
    badList = []

##Establish dictionary to hold correspondance of songs to passed-in keys
songsWithKeys = {False : 0, 'TOTAL' : 0}
numTimesKeyInSong = {}

##Prompt keys from user and read into list
print("List what words you want to look for in the songs")
print("It must be in a comma-separated list")
print("eg: wordone, wordtwo, ...")
keyStr = sys.stdin.readline().strip("\n")
keyList = keyStr.split(", ")

##Populate key dictionaries with default values
for key in keyList:
    songsWithKeys[key.capitalize()] = 0
    numTimesKeyInSong[key.capitalize()] = 0

##Put keys into a single string with no punctuation
newKeyStr = "".join(numTimesKeyInSong.keys())

##Prompt user for artists and read them in
print("List artists you want to look for in the same format or enter a URL with artists.")
print("Leave empty to look through all")
artStr = sys.stdin.readline().strip("\n")
artList = []

##Establish start time of the computation
t=time.time()

##Set up url opener to be able to read lyric data from metrolyrics
opener = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
initChar = '0'

##If specific artists were named
if (artStr != ""):
    
    ##Check if a URL was passed in
    if '.com' in artStr or '.org' in artStr or '.net' in artStr:
        
        ##Open the URL to search for artists
        x = opener.request('GET', artStr)
        bigData = str(x.data).lower()
        x.close()
        print("Searching for artists alphabetically...")
        initChar = '0'
        bigData = bigData.lower()

        ##Reformat without punctuation for easier searching
        if "p!nk" in bigData:
            artList.append("pink")
        remChar = ['!', '.', '+ ', '\'', '/']
        for ch in remChar:
            bigData = bigData.replace(ch, '')

        ##Search for all validated artists in the artist list
        for artist in validArtists:
            if (artist.replace("-", " ") in bigData.lower() and artist not in badList):
                artList.append(artist)
            if (artist[0] != initChar):
                initChar = artist[0]
                print("\t\tCurrently on "+initChar+". Found "+str(len(artList))+" artists so far.")
        print("Found "+str(len(artList))+" artists on page")

        ##Display all artists found if the number is low enough and user desires
        intake = 'y'
        if (len(artList) > 200):
            print("There are "+str(len(artList))+" artists. Would you like to see them (y/n)?")
            intake = sys.stdin.readline().strip("\n")
        if intake[0].lower() == 'y':
            print("\t".join(artList))

        ##Prompt for more artists if some were mised
        theURL = artStr
        print("Add additional artists in the prompt below in a comma-separated list")
        intake = sys.stdin.readline().strip("\n")

        ##Convert format read in to internally consistent format and add to list of artists
        if intake != "":
            artStr = intake.replace(" ", "-").lower()
            artList2 = artStr.split(",-")
            for musician in artList2:
                if musician not in artList:
                    artList.append(musician)

            ##Check to remove these artists from being skipped by the searcher
            ##Some artists have names close to HTML elements, so these are often skipped
            print("Would you like to remove these artists from the blacklist?\n(y,n):")
            yOrN = sys.stdin.readline().strip("\n").lower()
            if yOrN[0] == 'y':
                for musician in artList2:
                    if musician in badList:
                        badList.remove(musician)

        ##Prompt to remove artists from the list
        print("Remove artists from the list of found artists in the prompt below in a comma-separated list")
        intake = sys.stdin.readline().strip("\n")
        if intake != "":
            artStr = intake.replace(" ", "-").lower()
            artList2 = artStr.split(",-")
            for musician in artList2:
                if musician in artList:
                    artList.remove(musician)

            ##Prompt to add these artists to the blacklist
            print("Would you like to add these artists to the blacklist?\n(y,n):")
            yOrN = sys.stdin.readline().strip("\n").lower()
            if yOrN[0] == 'y':
                for musician in artList2:
                    if musician not in badList:
                        badList.append(musician)
                        
    ##If the list of artists is not a url
    else:
        
        ##If it seems to be some sort of url, say it isn't
        if (artStr.find(".") > -1 and artStr.find(" ") == -1):
            print(artStr+" is not a valid URL")

        ##Remove some filler characters and create internally consistent list
        remChar = ['!', '.', '+ ']
        for ch in remChar:
            artStr = artStr.replace(ch, '')
        artStr = artStr.replace(" ", "-").lower()
        artList = artStr.split(",-")
        
##If no artists are listed, create a blank list
else:
    artList = []

##Sort alphabetically for easier searching
artList.sort()

##Remove blank value from list
if '' in artList:
    artList.remove('')

##If specific artists were given
if (len(artList) > 0):

    ##Display the list of artists given and save the length
    print(', '.join(artList))
    inLen = len(artList)

    ##Iterate through the artists
    for val in artList:
        
        ##Check if artist is in the database
        if (val not in validArtists):
            ##Notify user of the new artist
            print("New artist found: "+val)
            print("Adding to database...")

            ##Initialize relevant variables
            artistValid = False
            songList = []

            ##Iterate through 20 pages of lyrics results
            for num in range(1, 20):
                
                ##Attempt to open the page that contains all the songs
                try:
                    rawData = opener.request('GET', "https://www.metrolyrics.com/"+val+"-alpage-"+str(num)+".html", retries=5)
                    data = str(rawData.data)
                    rawData.close()
                    invalid = False
                    
                ##Break the loop if the page is invalid
                except urllib3.exceptions.MaxRetryError:
                    print("Not valid")
                    invalid = True
                    invalidArtists.append(val)
                    data = ""
                    break

                ##Split the webpage at a keyword before song titles to get the list of songs on it
                dataList = data.split("www.metrolyrics.com/")

                ##Remove the first listing since it is invalid
                dataList.pop(0)

                ##Initialize relevant variables
                limitReached = False
                oldLen = len(songList)
                artistValid = len(songList) > 0

                ##Iterate through the list that contains song titles
                for i in dataList:

                    ##Establish a variable to hold the song title
                    thisSong = ""

                    ##Check if the data chunk is large enough to be holding a song title
                    if (i.find(val) > 4):

                        ##Iterate through each letter, one at a time
                        for letter in i:

                            ##Break if a / is found
                            if (letter == '/'):
                                break

                            ##Add letters to the title until a . is reached
                            if (letter != '.'):
                                thisSong += letter

                            ##Once a . is reached
                            else:
                                
                                ##Titles are always hyphenated, so check if any hyphens exist
                                ##No hyphens means the title is not relevan actual song title
                                if (thisSong.find("-") == -1):
                                    break
                                
                                else:
                                    ##Replace an invalid character that occasionally occurs
                                    thisSong.replace('%26-', '')

                                    ##Check if song is in the list of valid songs
                                    try:
                                        songList.index(thisSong)
                                    except:
                                        ##Add it if it isn't
                                        songList.append(thisSong)
                                        print(thisSong)
                                    ##End the loop of finding song titles
                                    break
                                
                ##If no new songs were added this iteration, break
                if (len(songList) == oldLen):
                    print(num)
                    break

            ##Display the number of songs found
            print("Found "+str(len(songList))+" songs by "+val)
            print("Reading site and adding to database")

            ##Establish a copy of the list of songs for iterating purposes
            newSongList = []
            for song in songList:
                newSongList.append(song)

            ##Iterate through all songs found
            for song in newSongList:

                ##Attempt to open the page with the lyric data
                try:
                    rawData = opener.request('GET', "http://www.metrolyrics.com/"+song+".html")
                    data = str(rawData.data).lower()
                    validSong = True
                except IOError:
                    ##Note if invalid webpage
                    print("Lost Internet Connection. Skipping Song "+str(song))
                    data = ""
                    validSong = False

                ##metrolyrics does not throw a solid 404 error when an address is incorrect
                ##Search for their common error messages
                validSong = validSong and data.find("hmm, that's weird") == -1 and data.find("please add them") == -1 and data.find("first to add these lyrics") == -1
                validSong = validSong and data.find("first to add these lyrics for us") == -1 and data.find("missing these lyrics") == -1 and data.find("authorized to display these") == -1
                validSong = validSong and data.find("we don't have these lyrics") == -1 and data.find("don't have the lyrics") == -1

                ##If no errors were found
                if (validSong):

                    print(song)

                    ##Remove html formatting, usually 4 sections
                    ####Remove fluff section 1
                    data = data.replace(data[0:data.find("<!-- first section -->")], "")
                    ####Remove fluff section 2
                    startToRemove = data.find("<!--widget - related-->")
                    endToRemove = data.find("<!-- second section -->")
                    if (startToRemove != -1 and endToRemove != -1):
                        data = data.replace(data[startToRemove : endToRemove], '')
                    ####Remove fluff section 3
                    secStartToRemove = data.find("<!--widget - photos-->")
                    secEndToRemove = max(-1, data.find("<!-- third section -->"))
                    if (secStartToRemove != -1):
                        data = data.replace(data[secStartToRemove : secEndToRemove], '')
                    ####Remove fluff section 4
                    thiStartToRemove = data.find("<!--bottom mpu-->")
                    if (thiStartToRemove != -1):
                        data = data.replace(data[thiStartToRemove : -1], "")

                    ##Establish that the artist has at least one song with posted lyrics
                    ##Sometimes, artists will be listed with songs, but none will have lyrics
                    artistValid = True

                    ##Remove other excess formatting
                    ####Remove newlines
                    while('\\n' in data):
                        data = data.replace('\\n', " ")
                    ####Remove everything in angle brackets
                        
                    while('<' in data):
                        data = data.replace(data[data.find('<'):data.find('>')+1], "  ")
                    ####Remove all backslashes
                    while('\\' in data):
                        data = data.replace('\\', '')

                    ##Save the extracted data for later use
                    x = open("lyrics\\"+song+".txt", "w+")
                    x.write(data)
                    x.close()

                ##If the song is invalid, remove it from the list
                else:
                    songList.pop(songList.index(song))

            ##After all songs have been checked, see if the artist is still considered valid
            if (artistValid):

                ##Add the new songs and artist to the saved list
                validArtists.append(val)
                for song in songList:
                    if (song not in totalValid):
                        totalValid.append(song+".txt")

                ##Display all new songs found
                print("Successfully found "+str(len(songList))+" valid songs by "+val)
                print(", ".join(songList).replace(val, ''))

            ##If the artist is invalid, record that
            else:
                print("Found no valid songs by "+val)
                invalidArtists.append(val)
                artList.remove(val)

    ##If no valid artists were found in the list of artists provided, end the program
    if (len(artList) == 0):
        print("No songs exist by that artist. Stopping program.")
        time.sleep(5)
        raise IOError

##Duplicate the list of valid artists for iteration
newTotalValid = totalValid

##Attempt to remove the empty string from the list of artists
try:
    artList.remove('')
except ValueError:
    pass

##Iterate through the list of file names of all saved valid songs
for name in totalValid:

    ##Attempt to pull author from the file name
    try:
        author = name.replace(name[0:name.index("lyrics")], "")
        author = author.replace("lyrics-", '')
        author = author.replace(".txt", '')
    ##Establish author as invalid if unable to find it
    except ValueError:
        author = "remix-cover-version"

    ##Set up letter to tell how far along we are alphabetically on the list
    if (initChar != name[0]):
        initChar = name[0]
        print(name[0])

    ##Establish relevant variables
    containsKey = False
    countThisSong = False

    ##Check if the song is a cover or remix
    ##Covers do not count toward an artist's word distribution because they are not their work
    if (len(artList) > 0 and name.find("remix") == -1 and name.find("-cover-") == -1 and name.find("-version-") == -1):
        if (author in artList):
            countThisSong = True
    else:
        countThisSong = False

    ##If the song should be counted
    if (countThisSong):

        ##Open the text file for the song
        try:
            x = open("lyrics/"+name)
            data = x.read()
            x.close()
        except FileNotFoundError:
            print("Please do not delete songs from the lyrics directory")
            print("Skipping song "+name)
            next

        ##Count it toward the total number of songs
        songsWithKeys['TOTAL'] += 1

        ##Replace unnecessary punctuation for easier searching
        data = data.replace("'", "").replace(",", "").replace(".", "").replace(">", "")

        ##Iterate through given keys
        for key in keyList:
            ##Search for the key in the song
            val1 = data.find(" "+key.lower()+" ")
            val2 = data.find(">"+key.lower()+" ")
            val3 = data.find(" "+key.lower()+"s ")
            val4 = data.find(">"+key.lower()+"s ")

            ##If a key is found, record it, print the key, song name, and context
            if (val1 > 0 or val2 > 0 or val3 > 0):
                val = max(val1, val2, val3, val4)
                songsWithKeys[key.capitalize()] += 1
                numTimesKeyInSong[key.capitalize()] += len(data[val-1: -1].split(key))-1
                print('\t'+key+'\t'+name)
                print('\n\t'+ data[val-15:val+15] + '\n')
                containsKey = True

        ##If none of the keys were found at all, record that
        if (not containsKey):
            songsWithKeys[False] += 1

##If there are a small number of artists            
if (len(artList) > 0 and len(artList) < 10):

    ##Format the list of artists for use in the filename for the results
    formatArtList = []
    for art in artList:
        allNamesArt = art.split("-")
        newArt=""
        for nome in allNamesArt:
            newArt += nome.capitalize()
        formatArtList.append(newArt)
    byList = "by"+"".join(formatArtList)

##If all artists are searched, note that in the results filename
elif len(artList) == 0:
    byList = "byAllArtists"

##If a bunch of artists are searched, save the url in the results filename
elif (len(artList) < 60000 and theURL != ""):
    theURL = theURL.replace(".html", "")
    while "." in theURL:
        theURL = theURL.replace(theURL[0:theURL.find(".")+3], "")
    theURL = theURL.replace("/", "-")
    byList = "from"+theURL

##If a bunch of artists are manually entered, save the first one and note 'and more' in the results filename
else:
    byList = "by"+artList[0]+"AndMore"

##Save the results
x = open("Data By Key/numSongsWith"+newKeyStr+byList+".txt", "w")
x.write(str(songsWithKeys))
x.close()
x = open("Data By Key/timesInSong"+newKeyStr+byList+".txt", "w")
x.write(str(numTimesKeyInSong))
x.close()

##Save updated artist and song lists
validArtists.sort()
x = open("Metadata/validSongsList.txt", "w")
x.write(str(totalValid))
x.close()
x = open("Metadata/validArtists.txt", "w")
x.write(str(validArtists))
x.close()
x = open("Metadata/invalidArtists.txt", "w")
x.write(str(invalidArtists))
x.close()
x = open("Metadata/badArtistList.txt", "w")
x.write(str(badList))
x.close()

##Display results file location
print("Data saved to /Data By Key/numSongsWith"+newKeyStr+""+byList+".txt")
print("and /Data By Key/timesInSong"+newKeyStr+byList+".txt")
print("This analysis took "+str(time.time() - t)+" seconds")
input("hit enter to end the program")
