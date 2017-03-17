from scrape import Scrape
from pymongo import MongoClient
import json
import time
import db
from db import Document
from django.db import transaction


# class Index:
#     def __init__(self):
#         self.index = dict()
#
#     def update_index(self, token, file_name, count, tags):
#         # Updating the list of documents if the token is already present in the index
#         if token in self.index:
#             self.index[token].append({
#                 'file_name': file_name,
#                 'count': count,
#                 'tags': tags
#             })
#         # Creating a new entry for the token
#         else:
#             self.index[token] = [{
#                     'file_name': file_name,
#                     'count': count,
#                     'tags': tags
#             }]
#
#     def write_to_mongo(self):
#         # Creating a MongoClient and accessing the index collection
#         client = MongoClient('mongodb://127.0.0.1:27017')
#         db = client['cs222']
#         index = db['index']
#
#         # Writing each token and the associated documents into the mongoDB collection
#         for token in self.index:
#             index.insert({
#                 'token': token,
#                 'documents': self.index[token]
#             })

client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs221']
terms_coll = db['terms_stemmed']
documents_coll = db['documents']

def scrape_and_index():
    prefix = 'WEBPAGES_RAW/'

    with open(prefix + 'bookkeeping.json', 'r') as file_handle:
        urls = json.load(file_handle)

    # index = Index()

    count = 0
    start_time = time.time()
    terms = []
    documents = []
    for key in urls:
        file_name = prefix + key
        # print 'Processing ', file_name, ' ', format(count/374.97, '.2f'), ' % done'
        s = Scrape(file_name, ['a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'p'])
        # document = Document(doc=key, url=urls[key])
        document = {'doc': key, 'url': urls[key]}
        document_terms = s.parse_content(document)

        terms.extend(document_terms)
        documents.append(document)
        # s.parse_content()
        # tags = s.get_token_tags()
        # tokens = s.get_token_frequencies()

        # for token in tokens:
        #     index.update_index(token, key, tokens[token], list(tags[token]))

        count += 1

        if count % 500 == 0:
            write_to_disk(documents, terms)
            print '=' * 30
            print 'Documents parsed = ', format(count / 374.97, '.2f'), ' % done'
            print 'Write to Disk Successful'
            print 'Time taken (seconds)\t:\t:', str((time.time() - start_time))
            print '=' * 30
            documents = []
            terms = []

    print 'Time taken (seconds)\t:\t"', str((time.time() - start_time))

    write_to_disk(documents, terms)
    # return documents, terms
    # index.write_to_mongo()


# @transaction.atomic
def write_to_disk(documents, terms):
    documents_coll.insert_many(documents)
    # for document in documents:
        # document.save()
    terms_coll.insert_many(terms)
    # for term in terms:
        # term.save()

if __name__ == '__main__':
    scrape_and_index()
    # write_to_disk(all_documents, all_terms)



# token = 'apple'
# record = index.find_one({"token": token})
# if record is None:
#     index.insert({"token": token, "count": 0})
# else:
#     print record
#     record['count'] += 1
#     index.update({'token': token}, {"$set": record}, upsert=False)

