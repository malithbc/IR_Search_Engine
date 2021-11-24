from elasticsearch import Elasticsearch, helpers
import json
import re
from googletrans import Translator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

es = Elasticsearch(['http://elastic:F88Am3PETDCfUp1tKJmb@localhost:9200'],timeout=30)


def translate_to_english(value):
	translator = Translator()
	english_term = translator.translate(value, dest='en')
	return english_term.text


def modify_text(item):
    item = item.replace('[', '')
    item = item.replace(']', '')
    item = item.replace('"', '')
    item = item.replace("'", '')       
    item = item.replace('\\', '')
    item = item.replace('t', '')
    item = item.replace('\xa0', '')
    return item


def post_processing_text(results):
    actors_list = []
    for i in range(len(results['hits']['hits'])) :
        School_en = json.dumps(results['hits']['hits'][i]['_source']["School_en"], ensure_ascii=False)
        School_en = modify_text(School_en)
        School_si = json.dumps(results['hits']['hits'][i]['_source']["School_si"], ensure_ascii=False)
        School_si = modify_text(School_si)
        Films_en = json.dumps(results['hits']['hits'][i]['_source']["Films_en"], ensure_ascii=False)
        Films_en = modify_text(Films_en)
        Films_si = json.dumps(results['hits']['hits'][i]['_source']["Films_si"], ensure_ascii=False)
        Films_si = modify_text(Films_si)
        Awards_en = json.dumps(results['hits']['hits'][i]['_source']["Awards_en"], ensure_ascii=False)
        Awards_en = modify_text(Awards_en)
        Awards_si = json.dumps(results['hits']['hits'][i]['_source']["Awards_si"], ensure_ascii=False)
        Awards_si = modify_text(Awards_si)
        Other_creation_en = json.dumps(results['hits']['hits'][i]['_source']["Other_creation_en"], ensure_ascii=False)
        Other_creation_en = modify_text(Other_creation_en)
        Other_creation_si = json.dumps(results['hits']['hits'][i]['_source']["Other_creation_si"], ensure_ascii=False)
        Other_creation_si = modify_text(Other_creation_si)
        Extra_profession_en = json.dumps(results['hits']['hits'][i]['_source']["Extra_profession_en"], ensure_ascii=False)
        Extra_profession_en = modify_text(Extra_profession_en)
        Extra_profession_si = json.dumps(results['hits']['hits'][i]['_source']["Extra_profession_si"], ensure_ascii=False)
        Extra_profession_si = modify_text(Extra_profession_si)

        results['hits']['hits'][i]['_source']["School_en"] = School_en
        results['hits']['hits'][i]['_source']["School_si"] = School_si
        results['hits']['hits'][i]['_source']["Films_en"] = Films_en
        results['hits']['hits'][i]['_source']["Films_si"] = Films_si
        results['hits']['hits'][i]['_source']["Awards_en"] = Awards_en
        results['hits']['hits'][i]['_source']["Awards_si"] = Awards_si
        results['hits']['hits'][i]['_source']["Other_creation_en"] = Other_creation_en
        results['hits']['hits'][i]['_source']["Other_creation_si"] = Other_creation_si
        results['hits']['hits'][i]['_source']["Extra_profession_en"] = Extra_profession_en
        results['hits']['hits'][i]['_source']["Extra_profession_si"] = Extra_profession_si

        actors_list.append(results['hits']['hits'][i]['_source'])
    aggregations = results['aggregations']
    actors = aggregations['name']['buckets']
    films = aggregations['film']['buckets']
    awards = aggregations['award']['buckets']
    other = aggregations['other']['buckets']

    return actors_list, actors, films, awards, other


def search_text(search_term):
    results = es.search(index='index-actors',doc_type = 'sinhala-actors',body={
        "size" : 500,
        "query" :{
            "multi_match": {
                "query" : search_term,
                "type" : "best_fields",
                "fields" : [
                    "Name_en", "Name_si", "Films_en","Films_si","Awards_en", 
                    "Awards_si", "Other_creation_en","Other_creation_si","Description_en", "Description_si"]
                    
            }
        },
        "aggs": {
            "name": {
                "terms": {
                    "field": "Name_si.keyword",
                    "size" : 15    
                }        
            },
            "film": {
                "terms": {
                    "field":"Films_si.keyword",
                    "size" : 15
                }             
            },
            "award": {
                "terms": {
                    "field":"Awards_si.keyword",
                    "size" : 15
                }             
            },
            "other": {
                "terms": {
                    "field":"Other_creation_si.keyword",
                    "size" : 15
                }             
            },

        }

    })

    actors_list, actors, films, awards, other_creations = post_processing_text(results)
    return actors_list, actors, films, awards, other_creations


def search_filter_text(search_term, actor_filter, film_filter, award_filter, other_creation_filter):
    must_list = [{
                    "multi_match": {
                        "query" : search_term,
                        "type" : "best_fields",
                        "fields" : [
                            "Name_en", "Name_si", "Films_en","Films_si","Awards_en", 
                    "Awards_si", "Other_creation_en","Other_creation_si","Description_en", "Description_si"]
                            
                    }
                }]
    if len(actor_filter) != 0 :
        for i in actor_filter :
            must_list.append({"match" : {"Name_si": i}})
    if len(film_filter) != 0 :
        for i in film_filter :
            must_list.append({"match" : {"Films_si": i}})
    if len(award_filter) != 0 :
        for i in award_filter :
            must_list.append({"match" : {"Awards_si": i}})
    if len(other_creation_filter) != 0 :
        for i in other_creation_filter :
            must_list.append({"match" : {"Other_creation_si": i}})
    results = es.search(index='index-actors',doc_type = 'sinhala-actors',body={
        "size" : 500,
        "query" :{
            "bool": {
                "must": must_list
            }
        },
        "aggs": {
            "name": {
                "terms": {
                    "field": "Name_si.keyword",
                    "size" : 15    
                }        
            },
            "film": {
                "terms": {
                    "field":"Films_si.keyword",
                    "size" : 15
                }             
            },
            "award": {
                "terms": {
                    "field":"Awards_si.keyword",
                    "size" : 15
                }             
            },
            "other": {
                "terms": {
                    "field":"Other_creation_si.keyword",
                    "size" : 15
                }             
            },

        }
    })

    actors_list, actors, films, awards, other_creations = post_processing_text(results)
    return actors_list, actors, films, awards, other_creations


def search_query(search_term):
    print("hhhhhhhhhhhhhh")
    actors_list, actors, films, awards, other_creations = search_text(search_term)

    return actors_list, actors, films, awards, other_creations


def search_query_filtered(search_term, actor_filter, film_filter, award_filter, other_creation_filter):
    actors_list, actors, films, awards, other_creations = search_filter_text(search_term, actor_filter, film_filter, award_filter, other_creation_filter)

    return actors_list, actors, films, awards, other_creations
    
    
            







    
