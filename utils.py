import requests
import json
import streamlit as st
import time
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='info.log', encoding='utf-8', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
CONST_BASEURL = 'https://swapi.dev/api/'

# Function Name: getDataList()
# Arguments:     url: string
#                sesh: Session object
#                results: list
#                resultsMap: hash map
#                identifier: string
# Returns:       0 on fail
# Purpose:       A recursive function that takes the provided URL
# and returns the associated json data, which is then appended to 
# results. This function will call itself until the 'next' field 
# in the returned json is of type None. Once that happens,
# the data accumulated in results is added to the resultsMap,
# where the key is identifier (name of the page queried) and
# the value is total list of results.
def getDataList(url, sesh, results, resultsMap, identifier):
    next = None
    headers = {'Accept-Encoding': 'br'}
    r = sesh.get(url, headers=headers)
    #Only proceed if the request was successful
    if (r.status_code == 200):
        data = json.loads(r.text)
        next = data['next']
        results += data['results']
    else:
        # Request failed, log a generic message and the accompanying error code for trouble shooting. 
        logger.info('Could not retrieve data. ErrCode: ' + str(r.status_code))
        return 0


    if next != None:
        # Recursive part of the function. Re-use both the running list and the session to reduce
        # run-time and memory usage. 
        logger.info("Fetching next character page...")
        getDataList(next, sesh, results, resultsMap, identifier)
    else:
        # Assign the final list. 
        resultsMap[identifier] = results

# Function Name: createDataMap()
# Arguments:     dataList: list
#                dataMap: hash map
# Returns:       none
# Purpose:       This function will take the entire master list of data
# retrieved from the API and create a master hash table of it, where the 
# key is the url for that particular piece of data and the value is 
# simply the name (or title in the case of movies). The intended use for this
# is for easy lookup of values that are simply listed as their URL.
def createDataMap(dataList, dataMap):
    for data in dataList:
        url = str(data['url'])
        if 'name' in data:
            name = str(data['name'])
        elif 'title' in data:
            name = str(data['title'])

        dataMap[url] = name

# Function Name: replaceURLS()
# Arguments:     character: dictionary
#                dataMap: hash map
# Returns:       none
# Purpose:       Iterate though each key/value pair within character. If a value
# contains the base url (https://swapi.dev/api/) then, using the entire value as 
# a key lookup in dataMap, we locate the name (or title in the case of movies)
# and replace the url in character with the value taken from dataMap.
# Additionally, if any value is found to be [], then the value will simply be
# re-assigned to be ['Unknown']. If the value needs to be changed from ['Unknown'] to 
# something else, please update this function to do so. 
# The intention for this is to drastically reduce the number of API calls needed. 
def replaceURLS(character, dataMap):
    for key in character.keys():
        val = character.get(key)
        
        if type(val) is list:
            urlList = character.get(key)
            filmList = []
            if len(urlList) == 0:
                filmList.append('Unknown')
            else:
                for url in urlList:
                    filmList.append(dataMap[url])
            character[key] = filmList
        elif key != 'url':
            urlKey = character.get(key)
            substring = CONST_BASEURL

            if substring in urlKey:
                character[key] = dataMap[urlKey]

# Function Name: sortCharacters()
# Arguments:     characterList: list
#                dataMap: hash map
# Returns:       characterMap: hash map
# Purpose:       Iterate through the list of characters, which is retrieved from
# the API and found in the results hash map under the key 'people'. For each character,
# first call replaceURLS on it and update any value fields that are URLs.
# Then grab the value associated with the 'species' key. With this value, 
# check to see if it exists as a key in characterMap. If not, then create the 
# new key, create an empty list, append the character object to the list, and then assign
# the list to the new key. If the key does exist, append the character the existing list.
# Once finished, characterMap will contain every species as its own key, and the value of
# each key will be a list of characters that are of that species. 
def sortCharacters(characterList, dataMap):

    index = 0
    characterMap = dict()
    for character in characterList:
        # First replace all URLs with their associated name or title
        replaceURLS(character, dataMap)
        species = character.get('species')

        # Now we have the species, determine if a key needs to be added or updated
        if (index == 0 or (species[0] not in characterMap)):
            tempList = []
            tempList.append(character)
            characterMap[species[0]] = tempList
            if index == 0: index += 1
        else:
            tempList = characterMap.get(species[0])
            tempList.append(character)
            characterMap[species[0]] = tempList


    return characterMap

# Function Name: generateData()
# Arguments:     none
# Returns:       characterMap: hash map
# Purpose:       This function defines the urls needed to make requests to 
# in order to compile all necessary info to eventually display character details. 
# First we query all pages necessary, then we create a master hashMap, and finally we
# sort the data and return a characterMap, where the key is the species and the
# value is a list of characters that are of that species.
def generateData():
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
    dataMap = {}
    results = {}
    with requests.Session() as fetchSesh:   
        try:
            for identifier, url in urls.items():
                resultsList = []
                getDataList(url, fetchSesh, resultsList, results, identifier)

        except Exception as e:
            logger.info(f"An error occurred: {e}")

    # Compile master hash map of URLs/Names
    for identifier, data in results.items():
        createDataMap(data, dataMap)

    # Sort characters by species
    characterList = results.get('people')
    characterMap = sortCharacters(characterList, dataMap)

    return characterMap

# Function Name: runStreamlit()
# Arguments:     none
# Returns:       none
# Purpose:       This function is the show runner.First it will display a splash page
# complete with a loading wheel. Once generateData() finishes, a series of collapsed 
# dropdowns will appear, each labeled with a species. Clicking on that dropdown will
# display all the characters of that species. This saves on screen real esate and
# eliminates the need to re-gather data in order to re-draw the screen.  
def runStreamlit():
    st.title("Star Wars Character Explorer")
    st.subheader("Displaying all characters organized by species (Collapsible)")

    status_placeholder = st.empty()

    # Display a loading message while fetching data
    with st.spinner("Fetching data... Please wait!"):
        characterMap = generateData()

    status_placeholder.success("Data loaded successfully!")

    # Iterate over the species and characters
    for species, characters in characterMap.items():
        with st.expander(f"Species: {species}"):
            for character in characters:
                st.write(f"**Name:** {character['name']}  \n")
                st.write(f"Height: {character['height']},  Mass: {character['mass']}  \n")
                st.write(f"Gender: {character['gender']},  Homeworld: {character['homeworld']},  Birth Year: {character['birth_year']}  \n")
                st.write(f"Films: {character['films']}  \n")
                st.write(f"Vehicles: {character['vehicles']}  \n") 
                st.write(f"Starships: {character['starships']}  \n")
                st.write(f"Created: {character['created']},  Edited: {character['edited']}  \n")
                st.write(f"URL: {character['url']}")
                st.write("---")  # Divider for readability

    # Closing note
    st.write("### End of the character list")

    # Remove success banner after a time
    time.sleep(3)
    status_placeholder.empty()