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


# def intent_classifier(search_term):

#     select_type = False
#     resultword = ''

#     # keyword_top = ["top", "best", "popular", "good", "great"]
#     # keyword_song = ["song", "sing", "sang", "songs", "sings"]
#     search_term_list = search_term.split()
#     for j in search_term_list : 
#         documents = [j]
#         # documents.extend(keyword_top)
#         # documents.extend(keyword_song)
#         tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#         tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

#         cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)
#         similarity_list = cs[0][1:]

#         for i in similarity_list :
#             if i > 0.8 :
#                 select_type  = True
#     if select_type :
#         querywords = search_term.split()
#         querywords  = [word for word in querywords if word.lower() not in keyword_top]
#         querywords  = [word for word in querywords if word.lower() not in keyword_song]
#         resultword = ' '.join(querywords)

    
#     return select_type,  resultword


# def top_most_text(search_term):

#     with open('song-corpus/songs_meta_all.json') as f:
#         meta_data = json.loads(f.read())

#     artist_list = meta_data["Artist_en"]
#     genre_list = meta_data["Genre_en"]
#     music_list = meta_data["Music_en"]
#     lyrics_list = meta_data["Lyrics_en"]

#     documents_artist = [search_term]
#     documents_artist.extend(artist_list)
#     documents_genre = [search_term]
#     documents_genre.extend(genre_list)
#     documents_music = [search_term]
#     documents_music.extend(music_list)
#     documents_lyrics = [search_term]
#     documents_lyrics.extend(lyrics_list)
#     query = []
#     select_type = False

#     size = 100
#     term_list = search_term.split()
#     print(term_list)
#     for i in term_list:
#         if i.isnumeric():
#             size = int(i)

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_artist)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]

#     max_val = max(similarity_list)
#     other_select = False
#     if max_val >  0.85 :
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Artist_en": artist_list[i]}})
#         select_type = True
#         other_select = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_genre)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]

#     max_val = max(similarity_list)
#     if max_val >  0.85 :
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Genre_en": genre_list[i]}})
#         select_type = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_music)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Music_en": music_list[i]}})
#         select_type = True
#         other_select = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_lyrics)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Lyrics_en": lyrics_list[i]}})
#         select_type = True
#         other_select = True
    
#     if select_type != True :
#         query.append({"match_all" : {}})

#     print(query)
#     results = es.search(index='index-songs',doc_type = 'sinhala-songs',body={
#         "size" : size,
#         "query" :{
#             "bool": {
#                 "must": query
#             }
#         },
#         "sort" :{
#             "views": {"order": "desc"}
#         },
#         "aggs": {
#             "genre": {
#                 "terms": {
#                     "field": "Genre_si.keyword",
#                     "size" : 15    
#                 }        
#             },
#             "artist": {
#                 "terms": {
#                     "field":"Artist_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "music": {
#                 "terms": {
#                     "field":"Music_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "lyrics": {
#                 "terms": {
#                     "field":"Lyrics_si.keyword",
#                     "size" : 15
#                 }             
#             },

#         }
#     })
#     list_songs, artists, genres, music, lyrics = post_processing_text(results)
#     return list_songs, artists, genres, music, lyrics

# def top_most_filter_text(search_term, artist_filter, genre_filter, music_filter, lyrics_filter):

#     with open('song-corpus/songs_meta_all.json') as f:
#         meta_data = json.loads(f.read())

#     artist_list = meta_data["Artist_en"]
#     genre_list = meta_data["Genre_en"]
#     music_list = meta_data["Music_en"]
#     lyrics_list = meta_data["Lyrics_en"]

#     documents_artist = [search_term]
#     documents_artist.extend(artist_list)
#     documents_genre = [search_term]
#     documents_genre.extend(genre_list)
#     documents_music = [search_term]
#     documents_music.extend(music_list)
#     documents_lyrics = [search_term]
#     documents_lyrics.extend(lyrics_list)
#     query = []
#     select_type = False
#     size = 100
#     term_list = search_term.split()
#     for i in term_list:
#         if i.isnumeric():
#             size = i

#     if len(artist_filter) != 0 :
#         for i in artist_filter :
#             query.append({"match" : {"Artist_si": i}})
#     if len(genre_filter) != 0 :
#         for i in genre_filter :
#             query.append({"match" : {"Genre_si": i}})
#     if len(music_filter) != 0 :
#         for i in music_filter :
#             query.append({"match" : {"Music_si": i}})
#     if len(lyrics_filter) != 0 :
#         for i in lyrics_filter :
#             query.append({"match" : {"Lyrics_si": i}})


#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_artist)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     other_select = False
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Artist_en": artist_list[i]}})
#         select_type = True
#         other_select = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_genre)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]

#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Genre_en": genre_list[i]}})
#         select_type = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_music)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Music_en": music_list[i]}})
#         select_type = True
#         other_select = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_lyrics)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False :
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Lyrics_en": lyrics_list[i]}})
#         select_type = True
#         other_select = True
    
#     if select_type != True :
#         query.append({"match_all" : {}})

#     print(query)
#     results = es.search(index='index-songs',doc_type = 'sinhala-songs',body={
#         "size" : 500,
#         "query" :{
#             "bool": {
#                 "must": query
#             }
#         },
#         "sort" :{
#             "views": {"order": "desc"}
#         },
#         "aggs": {
#             "genre": {
#                 "terms": {
#                     "field": "Genre_si.keyword",
#                     "size" : 15    
#                 }        
#             },
#             "artist": {
#                 "terms": {
#                     "field":"Artist_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "music": {
#                 "terms": {
#                     "field":"Music_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "lyrics": {
#                 "terms": {
#                     "field":"Lyrics_si.keyword",
#                     "size" : 15
#                 }             
#             },

#         }
#     })
#     list_songs, artists, genres, music, lyrics = post_processing_text(results)
#     return list_songs, artists, genres, music, lyrics


def search_query(search_term):
    # english_term = translate_to_english(search_term)
    # select_type, strip_term = intent_classifier(english_term)  
    # if select_type :
    #     list_songs, artists, genres, music, lyrics = top_most_text(strip_term)
    # else :
    print("oooooo")
    actors_list, actors, films, awards, other_creations = search_text(search_term)

    return actors_list, actors, films, awards, other_creations


def search_query_filtered(search_term, actor_filter, film_filter, award_filter, other_creation_filter):
    # english_term = translate_to_english(search_term)
    # select_type, strip_term = intent_classifier(english_term)  
    # if select_type :
    #     list_songs, artists, genres, music, lyrics = top_most_filter_text(strip_term, artist_filter, genre_filter, music_filter, lyrics_filter)
    # else :
    actors_list, actors, films, awards, other_creations = search_filter_text(search_term, actor_filter, film_filter, award_filter, other_creation_filter)

    return actors_list, actors, films, awards, other_creations
    
    
            







    
