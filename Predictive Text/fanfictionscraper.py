import time, re, math, string, random, requests, tkinter
from tkinter.filedialog import askopenfilename

try:
    from bs4 import BeautifulSoup4
except:
    import os
    print("This program requires the BeautifulSoup module. This will attempt to install it")
    val=os.system('py -3 -m pip install bs4')
    if(val!= 0):
        os.system('python3 -m pip install bs4')
    from bs4 import BeautifulSoup

from urllib.request import urlopen

pun=string.punctuation
pun=pun.replace("'", '')

data = {'START':{}, '.':0}

##Define method to get parsed webpage data
def getSoupObject(url, parser="html.parser"):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    connected = False
    text=requests.get(
    url,
    proxies={'http': '192.168.20.130:8080',},
    headers=headers,
    timeout=5).text
    return BeautifulSoup(text, parser)

##Confirm that the code can get webpage data
l=getSoupObject('https://google.com')

##Load existing data to append to it
def load():
    ##Prompt for new data or edit existing 
    intake = input("Would you like to continue from an existing save file? (y/n)")
    if('y' in intake):
        ##Prompt for a file location
        tkinter.Tk().withdraw()
        filename = askopenfilename()
        while '\\' in filename:
            filename.replace('\\', '/')

        ##Open, read, and return the data for the selected files
        ##One file is base data used in predictive text, the other tracks what
        ##sites have already been visited
        pathParts = filename.split('/')
        pathParts[-1] = 'postCountFor'+pathParts[-1]
        postCountPath = '/'.join(pathParts)
        return [eval(open(filename, 'r').read()), eval(open(postCountPath, 'r').read()), filename]
    ##Start from scratch
    else:
        ##Establish a new filename and return blank data
        filename = 'defaultFanficDataFile'+str(int(time.time()))
        return [{'START': {}, '.': 0},0, filename]

##Save data to its files
def save(postCounter):
    ##save frequency data in pre-specified location
    toSave = open(locationToSave, 'w')
    toSave.write(str(data))

    ##save sites visited in a seperate pre-specified location
    pathParts = locationToSave.split('/')
    pathParts[-1] = 'postCountFor'+pathParts[-1]
    postCountPath = '/'.join(pathParts)
    
    savePostCount = open(postCountPath, 'w')
    savePostCount.write(str(postCounter))
    
##Get the webpage data for a fanfiction post
def postFinder(pnum):

    ##Establish relevant variables
    toReturn = []
    url = 'https://www.fanfiction.net/s/'+str(pnum)

    ##Get the webpage data and parse it
    page=getSoupObject(url)
    pageBits = page.findAll('div')

    ##Iterate through all bits of the page
    for i in pageBits:

        ##Check if story is valid
        if 'Story Not FoundStory is unavailable for reading.' in i.text:
            print('Story '+str(pnum)+' is not available')
            break

        ##Get only parts on the page that have story text and add them to the list of text data
        if i.has_attr('id'):
            if i.get('id') == 'storytext' or i.get('id') == 'storycontent':
                toReturn.append(i.text)
                print(len(toReturn))

    return toReturn

##Pull frequency data from the given list of texts
def scraper(messages=[]):
    ##Iterate through every text
    for m in messages:
        ##Split at all punctuation to get number of sentences
        sentences=re.split('\. |\? |! |\n |- ', m.lower())

        ##Iterate through all sentences
        for i in sentences:

            ##Duplicate variable for consistency
            thisSentence=i

            ##Remove all punctuation and newlines
            for j in pun:
                while j in thisSentence:
                    thisSentence=thisSentence.replace(j, ' ')
            while '\n' in thisSentence:
                thisSentence=thisSentence.replace('\n', ' ')

            ##Convert to ascii to remove special characters
            ## and split at every word
            words=thisSentence.encode('ascii', 'ignore').decode('ascii').split(' ')
            ##Remove the empty string
            while '' in words:
                words.remove('')

            ##Iterate through all words
            for count in range(0, len(words)):

                ##Remove special characters
                w=words[count].encode('ascii', 'ignore').decode('ascii')

                ##If there are no special characters, get the data
                if w.isprintable and w != '':

                    ##Add new element in data dictionary if a new word is found
                    if w not in list(data.keys()):
                        data[w] = {'.':0}

                    ##If the word is the first in the sentence
                    if count == 0:
                        ##Add it to the list of words that start sentences
                        ## if it's not already
                        if w not in list(data['START'].keys()):
                            data['START'][w] = 0

                        ##If the following word is new, add it to the list of words
                        ## that follow the current word
                        if len(words) >= 2 and words[count+1] not in list(data[w].keys()):
                                data[w][words[count+1]] = 0

                        ##Increment counter of words that start sentences by one for this word
                        data['START'][w]+=1

                        ##If there are more words, add the next one to the frequency dictionary
                        if len(words) >= 2:
                            data[w][words[count+1]]+=1

                    ##If this is not the first word in the sentence        
                    else:

                        ##Check if this is the last word
                        if count+1 == len(words):

                            ##Note in the frequencies that this word ends a sentence
                            if '.' not in list(data[w].keys()):
                                data[w]['.']=0
                            data[w]['.']+=1

                        ##If it's not the last word
                        else:
                            ##Count the following word in this word's frequency
                            if words[count+1] not in list(data[w].keys()):
                                data[w][words[count+1]] = 0
                            data[w][words[count+1]]+=1

        ##Print the total number of sentences checked
        print(sum(data['START'].values()))

##Establish the main loop
def main(postCounter=1):
    while True:
        ##Get next site worh of posts
        posts=postFinder(postCounter)

        ##Scrape the data if there is data to scrape
        if len(posts) > 0:
            scraper(posts)

        ##Increment to move to the next post
        postCounter+=1
        print(postCounter)

        ##Save the data every 20 posts
        if postCounter % 20 == 0:
            save(postCounter)

##Load existing data
allDat=load()

##Split loaded data to relevant variables
data=allDat[0]
already=allDat[1]
locationToSave = allDat[2]

print("Entering main loop")

print(already)

##Go through the main loop
main(already)
