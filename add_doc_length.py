from pymongo import MongoClient

# Creating a MongoClient and accessing the terms collection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs221']
terms_collection = db['terms']
documents_collection = db['documents']
documents_collection_2 = db['documents2']


def find_length_of_document(doc_id, tags):
    # Finding the number of tokens in a document
    return terms_collection.count({'doc': doc_id, 'tag_type': {'$in': tags}})

final_docs = []
for doc in documents_collection.find({}):
    doc['length1'] = find_length_of_document(doc['doc'], ['title'])
    doc['length2'] = find_length_of_document(doc['doc'], ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
    doc['length3'] = find_length_of_document(doc['doc'], ['p'])
    final_docs.append(doc)
    # documents_collection.update({"_id": doc["_id"]}, {"$set": {"length": length}})
documents_collection_2.insert_many(final_docs)
