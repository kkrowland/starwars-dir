# starwars-dir

RUNNING INSTRUCTIONS:
1. Install StreamLit by going to your console and typing 'pip install streamlit'
2. Please be sure that \Python\Scripts\ is included in your PATH variables.
    a. Please see this guide if it is not or you're unsure: https://realpython.com/add-python-to-path/
3. Navigate to the directory you downloaded this repository to. Be sure that both main.py and utils.py are in the same directory.
4. Once there, use your preffered console or python compiler and type the command 'streamlit run main.py'
5. This should automatically open up a tab in your currently open or preffered browser. 
6. Once data is finished being gathered and curated, a series of collapsable tabs should appear in the tab that was opened. 
7. Click through any of the tabs to expand them and see further information about the characters that are of that species.

Purpose: The purpose of this application is to display StarWars character information from the StarWars API (https://swapi.dev/).
The information is intended to be sorted by species. For example, if you were to look under the species "Droid",
you would find all the characters that the API has labeled as Droid. 

Approach: In order to reduce number of requests, and therefore decrease runtime, information is pulled by the page
as opposed to each individual URL that correlates to that specific item. The result is a series of hash maps that are
sorted by the page category you might find that info. For example, items like "Luke" or "Darth Vader" exist under the key 'people', while items like 'Tatooine' or 'Hoth' exist under the key 'planets'.

The main components of this application are the resultsMap, the dataMap, and the characterMap. 
resultsMap - A hashmap where the value is a list of objects, and the key is the page those objects were requested from.
dataMap - A master hashmap. The value is the URL unique to an object fetched from the API, and the name or title of that object. 
characterMap - A hashmap of the final product of the application, which is one where the value is a list of objects and the key is the species of those objects. 

Notable components of this application include:
- Use of Session() and Brotli for compression to speed up api requests/responses
- StreamLit to display organized data in a pleasent and readable format
- Recursion in the initial data gathering phase to eliminate the need for more global/constant variables. Increases readability of code and allows for scalability if the API ever adds more pages of information. 

Things I would have liked to do to improve this application:
1. Threading. I initially attempted to use threads to speed up the data fetching process. One thread for each URL that needed to be queried. But I was running into too many race conditions and cross-contamination of data and decided that correctness was more important than speed.
2. Although not what was asked of me, I would have liked to tinker more with StreamLit to increase readability, as well as create a loading bar so that the user can see how much longer they have to go before data is displayed. Alternatively, if I ever do get threading working I could also attempt to lazy load the page with data as it is received and processed. 

