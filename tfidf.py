from pymongo import MongoClient
import json
from math import log
from collections import Counter
import time

# Creating a MongoClient and accessing the terms collection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs221']
terms_collection = db['terms']
documents_collection = db['documents2']

NUMBER_OF_DOCUMENTS = len(terms_collection.distinct('doc'))
start_time = time.time()
DOCUMENT_LENGTHS = {}
for doc in documents_collection.find({}):
    DOCUMENT_LENGTHS[doc['doc']] = (doc['length1'], doc['length2'], doc['length3'])


def find_length_of_document(doc_id, tags=None):
    # Finding the number of tokens in a document
    # return terms_collection.count({'doc': doc_id})
    if tags is None:
        return DOCUMENT_LENGTHS[doc_id][0] + DOCUMENT_LENGTHS[doc_id][1] + DOCUMENT_LENGTHS[doc_id][2]
    if tags[0] == 'title':
        return DOCUMENT_LENGTHS[doc_id][0]
    elif tags[0] == 'p':
        return DOCUMENT_LENGTHS[doc_id][2]
    else:
        return DOCUMENT_LENGTHS[doc_id][1]


def find_document_frequency(term, tags=None):
    # Choosing the query depending on whether the tags have been mentioned or not
    if tags is None:
        query = {'term': term}
    else:
        query = {'term': term, 'tag_type': {'$in': tags}}

    return len(terms_collection.distinct('doc', query))


def idf(term, tags):
    # Finding the number of documents in which a term occurs
    document_frequency = find_document_frequency(term, tags)

    return 0 if document_frequency is 0 else log(NUMBER_OF_DOCUMENTS / float(document_frequency), 10)


def tf_idf(term, tags=None):

    # Choosing the query depending on whether the tags have been mentioned or not
    if tags is None:
        query = [
            {'$match': {'term': term}},
            {
                '$group': {
                    '_id': "$doc",
                    'count': {'$sum': 1}
                }
            }]
    else:
        query = [
            {'$match': {'term': term, 'tag_type': {'$in': tags}}},
            {
                '$group': {
                    '_id': "$doc",
                    'count': {'$sum': 1}
                }
            }]

    tf_idf_counter = Counter()
    term_counts = terms_collection.aggregate(query)
    idf_term = idf(term, tags)
    for obj in term_counts:
        tf = 1 + log(obj['count'] / float(find_length_of_document(obj['_id'], tags)), 10)
        tf_idf_counter[obj['_id']] = tf * idf_term

    return tf_idf_counter


# prefix = 'WEBPAGES_RAW/'
#
# with open(prefix + 'bookkeeping.json', 'r') as file_handle:
#     urls = json.load(file_handle)
#
# N = len(urls)
#
# count = 0
# for term in index.find():
#     df_t = len(term['documents'])
#     idf_t = log(N/df_t, 10)
#     term['idf_t'] = idf_t
#     for i in range(df_t):
#         tf = log(term['documents'][i]['count'] + 1, 10)
#         tf_idf = tf * idf_t
#         term['documents'][i]['tf_idf'] = tf_idf
#
#     # print term['token'], ' TF-IDF calculation'
#     index.update({'token': term['token']}, {"$set": term}, upsert=False)
#
#     count += 1
#     if count % 1000 == 0:
#         print count, ' terms have been evaluated'
