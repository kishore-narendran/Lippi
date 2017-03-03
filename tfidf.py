from pymongo import MongoClient
import json
from math import log

# Creating a MongoClient and accessing the index collection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs222']
index = db['tfidf']

prefix = 'WEBPAGES_RAW/'

with open(prefix + 'bookkeeping.json', 'r') as file_handle:
    urls = json.load(file_handle)

N = len(urls)

count = 0
for term in index.find():
    df_t = len(term['documents'])
    idf_t = log(N/df_t, 10)
    term['idf_t'] = idf_t
    for i in range(df_t):
        tf = log(term['documents'][i]['count'] + 1, 10)
        tf_idf = tf * idf_t
        term['documents'][i]['tf_idf'] = tf_idf

    # print term['token'], ' TF-IDF calculation'
    index.update({'token': term['token']}, {"$set": term}, upsert=False)

    count += 1
    if count % 1000 == 0:
        print count, ' terms have been evaluated'

