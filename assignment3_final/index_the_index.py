from pathlib import Path
import nltk
import json


# dictionary with terms as keys and location in the file as values
# 1. open the file that corresponds to the first letter of the term
# 2. seek to the location in the file that corresponds with the term in termLocations
# 3. read the line, which contains the documents and term frequencies
# 4. use json to load in the dictionary contained in the line 
def getTermLocations():
    termLocations = {}

    # for each file in index_by_letter
    indexes_file_path = Path("")
    for file_name in indexes_file_path.iterdir():
    
        if "json_index" in str(file_name):
            # if "json_index" in file_name
            with open(file_name) as json_file:
                # for each line in the file
                while json_file:
                    # get location
                    location = json_file.tell()
                    text = json_file.readline()
                    # if a line is empty, break
                    if text == "":
                        break

                    # get term
                    words = nltk.word_tokenize(text)
                    term = words[2]
                    
                    # store in termLocations
                    termLocations[term] = location

    return termLocations



if __name__ == "__main__":
    termLocations = getTermLocations()


    with open("json_index_a.txt") as file:
        file.seek(termLocations["argentin"])
        text = file.readline()
        print(text)
        termDict = json.loads(text)
        print(termDict)
        

        file.seek(termLocations["axe"])
        text = file.readline()
        print(text)
        termDict = json.loads(text)
        print(termDict)