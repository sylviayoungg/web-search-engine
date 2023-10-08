import nltk
from nltk.stem import PorterStemmer
import json
import math
import time

termLocations = None
urlDict = None
numDocs = 0

def flaskSearch(query, flaskTermLocations, flaskDict, flaskNum):
    #global index
    global termLocations
    global urlDict
    global numDocs
    termLocations = flaskTermLocations
    urlDict = flaskDict
    numDocs = flaskNum
    return search(query)

# function for calculating cosine similarity, using formula given in lecture slides
def cosSimilarity(v1, v2):
    return sum(x * y for x, y in zip(v1, v2)) / (math.sqrt(sum(x * y for x, y in zip(v1, v1))) * math.sqrt(sum(x * y for x, y in zip(v2, v2))))

def search(query):
    global index
    global numDocs
    # parse terms in query the same way that our files were parsed
    term_list = []
    
    tokens = nltk.word_tokenize(query)
        
    ps = PorterStemmer()
        
    for token in tokens:
        # Check that word is an alphanumeric
        if not token.isalpha():
            pass
        else:
            token = token.lower()
            token = ps.stem(token)
            
            term_list.append(token)

    terms = set(term_list)
    terms_set_list = list(terms)

    # list of sets of pages that words appear on
    page_sets = []
    # number of terms in the keyword
    term_len = len(terms)

    # assume that there will be results, but if not resultsBool will be set to False
    resultsBool = True

    # how to score td-idf scores ??
    # we want scores for each document, it does not matter which words appear in which
    # documents, we only care about overall score
    # key = docID, value = tf=idf score
    tf_idf_scores = {}

    doc_frequency = {}

    # for each term, get a set with the pages the term appears on, and add to page_sets
    for i in range(term_len):
        # if the first character of term is A-Z or a-z
        try:
            startingLetter = terms_set_list[i][0]
            #if ((startingLetter >= 65 and startingLetter <= 90) or (startingLetter >= 97 and startingLetter <= 122)):
            if (startingLetter.isalpha()): 
                file_name = "json_index_" + startingLetter + ".txt"

            # if the first character of term is not A-Z or a-z
            else:
                file_name = "json_index_misc.txt"

            # open desired file
            with open(file_name) as json_file:
                # find location to seek to, read line, then load in dictionary
                json_file.seek(termLocations[terms_set_list[i]])
                json_text = json_file.readline()
                termDict = json.loads(json_text)

            docFrequency = len(termDict[terms_set_list[i]].keys())
            doc_frequency[terms_set_list[i]] = docFrequency

            # calculate each document's tf-idf weight and store into vectors (lists)

            for docID, tf in termDict[terms_set_list[i]].items():

                tf_idf_score = (1 + math.log(tf, 10)) * math.log(numDocs/docFrequency, 10)

                if docID not in tf_idf_scores:
                    tf_idf_scores[docID] = [0] * term_len
                tf_idf_scores[docID][i] = tf_idf_score
        except KeyError:
            resultsBool = False


    # sort documents by cosine similarity score, then return results in that order
    if (len(tf_idf_scores) != 0):
        # calculate tf-idf weight of each term in query
        keyword_vector = []
        for term in terms:
            tf = 1 + math.log(term_list.count(term), 10)
            docFrequency = doc_frequency[term]
            keyword_vector.append(tf * math.log(numDocs/docFrequency, 10))
        cos_similarity = {}
        # calculate cosine similarity score for each document
        for docID in tf_idf_scores.keys():
            cos_similarity[docID] = cosSimilarity(keyword_vector, tf_idf_scores[docID])
        
        sorted_docs = sorted(cos_similarity, key=lambda k: cos_similarity[k], reverse=True)
        return [urlDict[doc] for doc in sorted_docs]
    return None


if __name__ == "__main__":
    
    # old code from full index
    # json_name = 'json_index.json'
    # with open(json_name, 'r') as json_file_load:
    #    index = json.load(json_file_load)

    # load in index of index and urlDict
    json_name = 'json_termLocations.json'
    with open(json_name, 'r') as json_file_load:
        termLocations = json.load(json_file_load)

    json_name = 'json_urlDict.json'
    with open(json_name, 'r') as json_file_load:
        urlDict = json.load(json_file_load)

    numDocs = len(urlDict)

    # get user input string
    query = input("Enter search query: ")

    # start timer
    start = time.time()

    sorted_docs = search(query)
    if sorted_docs is not None:
        for doc in sorted_docs:
            print(doc)
    else:
        print("Sorry, no page matched your keyword")

    # end timer
    end = time.time()
    print("Took", (end - start)*1000, "milliseconds for search results")

    # if there are results, find intersection of sets in page_sets
    """
    if resultsBool:
        if len(page_sets) > 1:
            # find intersection of sets 0 and 1, then intersect that with the remaining sets
            pages = page_sets[0].intersection(page_sets[1])
            for i in range(2, len(page_sets)):
                pages = pages.intersection(page_sets[i])
            # print url results
            for page in pages:
                print(urlDict[page])

        # if there is only one set, return urls from that set
        else:
            for page in page_sets[0]:
                print(urlDict[page])

    else:
        print("No results found")
    """