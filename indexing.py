from elasticsearch import Elasticsearch, helpers
import json

# es = Elasticsearch([{'host': 'localhost', 'port':9200}])
es = Elasticsearch(['http://elastic:F88Am3PETDCfUp1tKJmb@localhost:9200'], timeout=300)

def data_upload():
    with open('actors/actors.json') as f:
        data = json.loads(f.read())
    helpers.bulk(es, data, index='index-actors', doc_type='sinhala-actors')


if __name__ == "__main__":
    data_upload()

