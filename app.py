from elasticsearch import Elasticsearch, helpers
import json
from flask import Flask
from flask import flash, render_template, request, redirect, jsonify
import re
from googletrans import Translator
from search import search_query_filtered, search_query

es = Elasticsearch([{'host': 'localhost', 'port':9200}])
app = Flask(__name__)


global_search = "_"
global_actor = []
global_film = []
global_award = []
global_other = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global global_search
    global global_actor
    global global_film
    global global_award
    global global_other
    if request.method == 'POST':
        if 'form_1' in request.form:
            if request.form['nm']:
                search = request.form['nm']
                global_search = search
                print(global_search)
            else :
                search = global_search
            actors_list, actors, films, awards, other_creations = search_query(search)
            global_actor, global_film, global_award, global_other = actors, films, awards, other_creations
        elif 'form_2' in request.form:
            search = global_search
            actor_filter = []
            film_filter = []
            award_filter = []
            other_creation_filter = []
            for i in global_actor :
                if request.form.get(i["key"]):
                    actor_filter.append(i["key"])
            for i in global_film :
                if request.form.get(i["key"]):
                    film_filter.append(i["key"])
            for i in global_award:
                if request.form.get(i["key"]):
                    award_filter.append(i["key"])
            for i in global_other:
                if request.form.get(i["key"]):
                    other_creation_filter.append(i["key"])
            actors_list, actors, films, awards, other_creations = search_query_filtered(search, actor_filter, film_filter, award_filter, other_creation_filter)
        return render_template('index.html', actors = actors_list, name = actors, films = films, awards = awards, other_creations = other_creations)
    return render_template('index.html', actors = '', name = '',  films = '', awards = '', other_creations = '')

if __name__ == "__main__":
    app.run(debug=True)
