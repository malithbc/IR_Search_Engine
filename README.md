# Sinhala Actors/ Actresses Search Engine 

This repository contain source code for Sinhala actors and actresses search engine created using Python and Elasticsearch

## Directory Structure

The important files and directories of the repository is shown below

    ├── actors : Collected data from the [website](https://www.films.lk/) and Wikipedia                  
        ├── actors.json : contain the final actors and actresses set 
        ├── actors_meta_data.json : contain all meta date related to the actors
    ├── templates : UI related files  
    ├── app.py : Backend of the web app created using Flask 
    ├── indexing.py : File to upload data to elasticsearch cluster
    ├── search.py : Search functions used to classify user search phrases and elasticsearch queries
    ├── requirements.txt :  All installed libaries with version          


## Starting the web app

### Spinning the elasticsearch cluster

You can install elasticsearch locally or otherwise and spin up the elasticsearch cluster
For more details visit [website](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-install.html)

Once elasticsearch is install, start elasticsearch cluster on port 9200

### Getting started with the web app

```commandline
git clone https://github.com/malithbc/IR_Search_Engine.git

cd IR_Search_Engine-master

virtualenv -p python3 env

.\env\Scripts\activate - activate virtual environment in windows

source env/bin/activate - activate virtual environment in ubuntu

pip3 install -r requirements.txt

python indexing.py - generate indexing for the documents

python app.py
```

### To run the web scraper

Follow the above steps and execute `python app.py` command

## Data fields 

Each actors/ actresses contain subset of following data fields

1. Name - English 
2. Name - Sinhala
3. School - English
4. School - Sinhala
5. Description - Sinhala
6. Description - English
7. Birthday
8. First film - English
9. First film - Sinhala
10. Films - English
11. Films - Sinhala
12. Awards - English
13. Awards - Sinhala
14. Date of died
15. Other creations - English
16. Other creations - Sinhala
17. Extra profession - English
18. Extra profession - Sinhala
19. Number of acted films


## Data Collecting process

Collect Sinhala actors and actresses data from www.films.lk website and wikipedia. Collect all data into the excel sheet. Then generate actors.json file using python code.


## Search Process

### Indexing and quering

For indexing the data and querying the Elasticsearch is used and I have used the standard indexing methods,mapping and the analyzer provided in the Elasticsearch. When a user enters a query the related intent is identified and the search query is related to the intent is executed. Multi match query and bollean query are used for search data. The searching can be done related to name, description, films, awards, other creation fields. Also filtered queries are provided where users can filter the search result.

## Advance Features                  

* Intent Classification
    * Once the query is added, intent behind the query is found by intent classification. The intent could be simple text search or a select top type, etc. The intent classifier used word tokenization and text vectorization and cosine distance to classify intentens
* Bilingual support
    * The search engine supports queries in both Sinhala and English. User can type queries like Vijaya Nandasiri or විජය නන්දසිරි and expect to yield the same result.




