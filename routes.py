from flask import Flask, request, render_template
from form import SearchForm
from search import flaskSearch
import json
import time

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    #global index
    global termLocations
    global urlDict
    global numDocs
    form = SearchForm(request.form)

    if request.method == 'POST' and form.validate():
        # extract keyword
        keyword = request.form['keyword']
        start = time.time()
        result = flaskSearch(keyword, termLocations, urlDict, numDocs)
        end = time.time()
        print("Took", (end - start)*1000, "milliseconds for search results")
        return render_template('result.html', input=result)
    else:
        return render_template('search.html', form=form)

if __name__ == "__main__":
    json_name = 'json_termLocations.json'
    with open(json_name, 'r') as json_file_load:
        termLocations = json.load(json_file_load)

    json_name = 'json_urlDict.json'
    with open(json_name, 'r') as json_file_load:
        urlDict = json.load(json_file_load)

    numDocs = len(urlDict)
    print("Successfully imported index")
    app.run(host="0.0.0.0", port=8080)