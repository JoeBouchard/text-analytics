import random, string, tkinter
from tkinter.filedialog import askopenfilename

##open a data file at a given location
def load():
    tkinter.Tk().withdraw()
    filename = askopenfilename()
    return eval(open(filename, 'r').read())

##The data file contains a double-layered dictionary of words and the words 
## that often immediately follow them.
## {'word1' : {'word2' : 1, 'word3': 3, ...}

##This algorithm picks a weighted random word from the words (including the end
## of a sentence) that commonly follow the first word. Words that start sentences
## are listed as coming after 'START'. All other words are lowercase. After a 
## word is picked, it becomes the basis for the selection of the next word, 
## and its dictionary and values are usedto select the third word. This continues
## until the end sentence marker '.' is reached or the sentence gets to be 50
## words long

def sentenceMaker(toUse):
    
    ##Define useful variables
    toDisp = []
    keys = list(toUse['START'].keys())

    ##Pick the first word and add it to the list
    values=[]
    for i in keys:
        values.append((toUse['START'][i])**4)
    choice=random.choices(keys, weights=values)[0]
    toDisp.append(choice)

    ##Begin selection loop
    while choice != '.' and len(toDisp) < 50:

        ##Attempt to select a new word
        try:

            ##Get the words and their frequencies
            keys = list(toUse[choice].keys())
            values=[]
            for i in keys:
                values.append(toUse[choice][i])

            ##Select a word given the weighted list of keys
            choice=random.choices(keys, values)[0]

            ##Re-select the word until it gets to a valid word. Usually not necessary
            while choice == '' or (choice not in list(toUse.keys()) and choice != '.'):
                if choice != '.' and (choice not in list(toUse.keys()) or len(toUse[choice]) < 3 or len(wordFreqs[choice][2]) == 0):
                    choice2=choice
                    choice=random.choices(keys, values)[0]
                    if choice2 == choice:
                        choice = '.'
        ##Rarely used, but select the last one if something fails
        except:
            choice=keys[-1]

        ##Add the selected word to the sentence
        toDisp.append(choice)
    ##Print the full sentence
    print(' '.join(toDisp)+'\n')

##Prompt to open a data file
data=load()
print("%d total sentences parsed" % sum(data['START'].values()))

##Create 20 sentences
for sentence in range(0, 20):
    sentenceMaker(data)
