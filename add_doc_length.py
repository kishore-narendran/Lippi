from pymongo import MongoClient

# Creating a MongoClient and accessing the terms collection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs221']
terms_collection = db['terms']
documents_collection = db['documents']
documents_collection_1 = db['documents1']

def find_length_of_document(doc_id):
    # Finding the number of tokens in a document
    return terms_collection.count({'doc': doc_id})

final_docs = []
for doc in documents_collection.find({}):
    doc['length'] = find_length_of_document(doc['doc'])
    final_docs.append(doc)
    # documents_collection.update({"_id": doc["_id"]}, {"$set": {"length": length}})
documents_collection_1.insert_many(final_docs)
