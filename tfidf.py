from pymongo import MongoClient
import json
from math import log
from collections import Counter
import time

# Creating a MongoClient and accessing the terms collection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs221']
terms_collection = db['terms']
documents_collection = db['documents1']

NUMBER_OF_DOCUMENTS = len(terms_collection.distinct('doc'))
start_time = time.time()
DOCUMENT_LENGTHS = {}
for doc in documents_collection.find({}):
    DOCUMENT_LENGTHS[doc['doc']] = doc['length']
print "Find Document Lengths Time = ", str((time.time() - start_time))


def find_length_of_document(doc_id):
    # Finding the number of tokens in a document
    # return terms_collection.count({'doc': doc_id})
    return DOCUMENT_LENGTHS[doc_id]


def tf_normalized(term, doc_id, tf):
    document_length = float(find_length_of_document(doc_id))

    # Finding the count of terms in the given document
    if tf is not None:
        term_count = terms_collection.count({'term': term, 'doc': doc_id})
    else:
        term_count = tf

    return 0.0 if term_count is 0 else (1 + log(float(term_count) / document_length, 10))


def find_document_frequency(term):
    return len(terms_collection.distinct('doc', {'term': term}))


def idf(term):
    # Finding the number of documents in which a term occurs
    document_frequency = find_document_frequency(term)

    return 0 if document_frequency is 0 else log(NUMBER_OF_DOCUMENTS / float(document_frequency), 10)


# def tf_idf(term, doc_id, tf):
#     tf_score = tf_normalized(term, doc_id, tf)
#     idf_score = idf(term)
#     return tf_score * idf_score

def tf_idf(term):
    tf_idf_counter = Counter()
    term_counts = terms_collection.aggregate([
        {'$match': {'term': term}},
        {
            '$group': {
                '_id': "$doc",
                'count': {'$sum': 1}
            }
        }
    ])
    idf_term = idf(term)
    for obj in term_counts:
        tf = 1 + log(obj['count'] / float(find_length_of_document(obj['_id'])), 10)
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
