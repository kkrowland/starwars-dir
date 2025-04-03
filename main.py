import requests
from threading import Thread
import json

CONST_BASEURL = 'https://swapi.dev/api/'

def getDataList(url, sesh, results, resultsMap, identifier):
    
    next = None
    headers = {'User-Agent': 'my1-app'}
    r = sesh.get(url, headers=headers)
    #Only proceed if the request was successful
    if (r.status_code == 200):
        data = json.loads(r.text)
        next = data['next']
        print("Next value: " + str(next))
        results += data['results']
    else:
        # Request failed, log a generic message and the accompanying error code for trouble shooting. 
        print('Could not retrieve data. ErrCode: ' + str(r.status_code))
        return 0


    if next != None:
        # Recursive part of the function. Re-use both the running list and the session to reduce
        # run-time and memory usage. 
        print("Fetching next character page...")
        getDataList(next, sesh, results, resultsMap, identifier)
    else:
        # All done. No need to return anything else as we are passing characterList in by reference.
        resultsMap[identifier] = results

#Take all the data we received and create one master hash map, where the key is the url and the value is the name or title of that data. 
def createDataMap(dataList, dataMap):
    for data in dataList:
        url = str(data['url'])
        if 'name' in data:
            name = str(data['name'])
        elif 'title' in data:
            name = str(data['title'])

        dataMap[url] = name

def sortCharacters(characterList, speciesMap):

    # Iterate through characterList and check its 'species' field. 
    # Check to see if that species already exists in characterMap.
    # If it doesn't, create a new key-pair, where the species is the key and 
    # a list containing only the new character is the value.
    # If the species does exist already, simply append the character to the existing list. 
    index = 0
    characterMap = dict()
    for character in characterList:
        speciesURL = character.get('species')
        species = ''
        if(speciesURL):
            #Get returns a list, but we need it as a string to use as a key for the next map.
            speciesURL = speciesURL[0]
            speciesKey = str((speciesURL))
            species = speciesMap[speciesKey]
        else:
                species = 'Undefined'

        if (index == 0 or (species not in characterMap)):
            tempList = []
            tempList.append(character)
            characterMap[species] = tempList
            if index == 0: index += 1
        else:
            tempList = characterMap.get(species)
            tempList.append(character)
            characterMap[species] = tempList


    return characterMap

# Dict of URLS needed to fill in all data for characters
urls = {
    'people': CONST_BASEURL + 'people/',
    'species': CONST_BASEURL + 'species/',
    'planets': CONST_BASEURL + 'planets/',
    'vehicles': CONST_BASEURL + 'vehicles/',
    'films': CONST_BASEURL + 'films/',
    'starships': CONST_BASEURL + 'starships/'
}
resultsList = []
threads = []
speciesMap = {}
dataMap = {}
results = {}
with requests.Session() as fetchSesh:   
    try:
        for identifier, url in urls.items():
            thread = Thread(target=getDataList, args=(url, fetchSesh, resultsList, results, identifier))
            threads.append(thread)
            thread.start()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        for thread in threads:
            thread.join()

#Now we create one big hash map of URL/Names for easy look up when filling in data for reading later
for identifier, data in results.items():
    createDataMap(data, dataMap)

# charMap = sortCharacters(characterList=characterList, speciesMap=speciesMap)
