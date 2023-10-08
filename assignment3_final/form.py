from wtforms import (Form, validators, SubmitField, SearchField)

class SearchForm(Form):
    # textbox
    keyword = SearchField("Keyword: ", validators=[validators.InputRequired()])
    
    # submit button
    submit = SubmitField("Search")
