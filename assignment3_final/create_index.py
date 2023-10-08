from collections import deque
from pathlib import Path
import nltk
from nltk.stem import PorterStemmer
import json
from bs4 import BeautifulSoup
import ijson
import index_the_index

# main directory where JSON files are found
# testing with ANALYST but our assignment requires DEV
#directory = 'DEV'

# index is a dictionary where the key is a token and the value is a list of postings
# postings include a document name/id that the token was found in, along with
# tf-idf score for document
index = {}

# docID variable, when a new docID is assigned, this variable should be incremented
currentDocID = 0

urlDict = {}

# storage ID, increment to store in different locations
storeID = 0

# Posting class
"""
class Posting:
    
    # initialize with docID number and tf_idf_score
    def __init__(self, docID, tf_idf_score = 0):
        self.docID = docID
        self.tf_idf_score = tf_idf_score

    # add to frequency of token in document
    def increaseFrequency(self, scoreIncrease):
        self.tf_idf_score += scoreIncrease
"""

# previous code when using jsonmerge

# schema = {
#     "properties": {
#         "mergeStrategy": "objectMerge"
#     }
# }

# merger = Merger(schema)
# queue = deque()

# takes a relative directory path and indexes all of the files in it.
# recursively accesses files. if the given name is a directory, it is called again
def index_all_files(directory:str):
    global storeID
    global index

    # open up file path with all webpage files
    user_file_path = Path(directory)
    for file_name in user_file_path.iterdir():
        # if file_name is a file, then tokenize
        # after each chunk of 10,000 pages is indexed, send index to disk
        if currentDocID % 10000 == 0 and currentDocID != 0:
                index = dict(sorted(index.items()))
                store_disk()
                storeID += 1
                index.clear()
                print(len(index))
        if file_name.is_dir() == False:
            # tokenize file 
            index_file(file_name)

        # if file_name is a directory, then call function again to get to content in folder
        if file_name.is_dir() == True:
            index_all_files(file_name)


# combines all partial indexes and stores them as JSON in a new file
def combine_all():
    global storeID
    # use a queue to manage json to be merged until only 1 json file left (all merged)
    new_json = {}
    curr_word = ""
    location = []
    for i in range(storeID):
        location.append(0)

    # merge partial index based on initials, starting with a to z initials

    for c in range(97, 123):
        new_json.clear()
        curr_word = ""
        for i in range(storeID):
            j = 0
            json_name = 'json_storage' + str(i) + '.json'
            with open(json_name, 'rb') as json_file_load:
                parser = ijson.parse(json_file_load)
                for prefix, event, value in parser:
                    if j <= location[i]:
                        j += 1
                        continue

                    if event == 'end_map':
                        location[i] = j
                        continue
                    
                    if event == "start_map":
                        if len(prefix) > 0 and prefix[0] == chr(c):
                            curr_word = prefix
                            if prefix not in new_json:
                                new_json[prefix] = {}
                        else:
                            if ord(prefix[0]) > c:
                                break
                            else:
                                continue


                    if event == "map_key" and len(prefix) > 0 and prefix == curr_word:
                        new_json[prefix][value] = 0
                    if event == "number":
                        param = prefix.split('.')
                        if param[0] == curr_word:
                            new_json[param[0]][param[1]] = value
                    j += 1

        new_json = dict(sorted(new_json.items()))
        json_name = 'json_index_' + chr(c) + '.txt'
        with open(json_name, 'w') as json_file_dump:
            for k in new_json.keys():
                json_file_dump.write('{"' + k + '": ' + json.dumps(new_json[k]) + '}\n')


    # then work on words starting with non-english characters

    new_json.clear()
    curr_word = ""

    for i in range(storeID):
        j = 0
        json_name = 'json_storage' + str(i) + '.json'
        with open(json_name, 'rb') as json_file_load:
            parser = ijson.parse(json_file_load)
            for prefix, event, value in parser:
                if j <= location[i]:
                    j += 1
                    continue
                    
                if event == "start_map":
                    if len(prefix) > 0 and (ord(prefix[0]) < 97 or ord(prefix[0]) > 122):
                        curr_word = prefix
                        if prefix not in new_json:
                            new_json[prefix] = {}
                    else:
                        continue

                if event == "map_key" and len(prefix) > 0 and prefix == curr_word:
                    new_json[prefix][value] = 0
                if event == "number":
                    param = prefix.split('.')
                    if param[0] == curr_word:
                            new_json[param[0]][param[1]] = value
                j += 1

    new_json = dict(sorted(new_json.items()))
    json_name = 'json_index_misc.txt'
    with open(json_name, 'w') as json_file_dump:
        for k in new_json.keys():
            json_file_dump.write('{"' + k + '": ' + str(new_json[k]) + '}\n')


# indexes a single file given a file path
def index_file(file_path):
    global urlDict
    global currentDocID
    currentDocID += 1
    with open(file_path) as json_file:
        try:
            json_object = json.load(json_file)
            url = json_object['url']
            urlDict[currentDocID] = url

            content = json_object['content']
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            index_tokens(text,1)

            WeightedTitle=soup.findAll('title') #weight 10
            for Title in WeightedTitle:
                index_tokens(Title.get_text(),10)

            WeightedHeaderH1=soup.findAll('h1') #weight 9
            for H1 in WeightedHeaderH1:
                index_tokens(H1.get_text(),9)

            WeightedHeaderH2=soup.findAll('h2') #weight 8
            for H2 in WeightedHeaderH2:
                index_tokens(H2.get_text(),8)

            WeightedHeaderH3=soup.findAll('h3') #weight 7
            for H3 in WeightedHeaderH3:
                index_tokens(H3.get_text(),7)

            WeightedHeaderH4=soup.findAll('h4') #weight 6
            for H4 in WeightedHeaderH4:
                index_tokens(H4.get_text(),6)

            WeightedHeaderH5=soup.findAll('h5') #weight 5
            for H5 in WeightedHeaderH5:
                index_tokens(H5.get_text(),5)

            WeightedHeaderH6=soup.findAll('h6') #weight 4
            for H6 in WeightedHeaderH6:
                index_tokens(H6.get_text(),4)

            weightedTextBold=soup.findAll(['b','strong'])   #weight 5
            for Bold in weightedTextBold:
                index_tokens(Bold.get_text(),5)

            weightedTextItlaics=soup.findAll(['em','i'])    #weight 3
            for Italics in weightedTextItlaics:
                index_tokens(Italics.get_text(),3)
        except ValueError:
            # ValueError is thrown if the file is not in correct JSON format
            pass



# given a string and a weight, the tokens of the string are indexed 
def index_tokens(text,Weight):
    # grab current docID
    global currentDocID
    global index


    words = []
    words = nltk.word_tokenize(text)
    
    ps = PorterStemmer()
    
    for word in words:
        # Check that word is an alphanumeric
        if not word.isalpha():
            pass
        else:
            word = word.lower()
            word = ps.stem(word)
            # Increment word frequency if word already exits in dictionaries.
            if word in index.keys():
                if currentDocID in index[word]:
                    index[word][currentDocID] += Weight
                else:
                    index[word][currentDocID] = 1

            # Add word and set frequency to 1 if words does not already exist in dictionaries.
            else:
                index[word] = {}
                index[word][currentDocID] = 1



# Store indexed files in disk storage
def store_disk():
    global index

    json_name = 'json_storage' + str(storeID) + '.json'
    
    # Create json file for data storage
    with open(json_name, 'w') as json_file_dump:
        # Add data to json file
        json.dump(index, json_file_dump)

    index.clear()
    
    
# retrieve disk at storage id
def retrieve_disk(id: int):
    json_name = 'json_storage' + str(id) + '.json'
    with open(json_name, 'r') as json_file_load:
        return json.load(json_file_load)



def main():
    global currentDocID
    global index
    global storeID
    global urlDict
    # index all of the files in DEV
    index_all_files('DEV')

    # after all files have been indexed, send final partial index to disk
    index = dict(sorted(index.items()))
    store_disk()

    # increment storeID for the id range of final merge
    storeID += 1

    # clear the index variable
    index.clear()
    # print number of unique words in index
    print(len(index))

    # combine all partial indexes and send to disk
    combine_all()

    # send urlDict to disk in JSON format
    json_name = 'json_urlDict.json'
    
    # Create json file for data storage
    with open(json_name, 'w') as json_file_dump:
        # Add data to json file
        json.dump(urlDict, json_file_dump)

    # creating index of index, then storing termLocations dict
    # see index_the_index.py for more information
    json_name = 'json_termLocations.json'

    termLocations = index_the_index.getTermLocations()

    # store termLocations in json to be retrieved later
    with open(json_name, 'w') as json_file_dump:
        # Add data to json file
        json.dump(termLocations, json_file_dump)
    
    print(currentDocID)


if __name__ == "__main__":
    main()
