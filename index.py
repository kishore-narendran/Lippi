from scrape import Scrape
from pymongo import MongoClient
import json
import time


# Creating a MongoClient and accessing the index collection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['cs222']
index = db['index']

prefix = 'WEBPAGES_RAW/'

with open(prefix + 'bookkeeping.json', 'r') as file_handle:
    urls = json.load(file_handle)

count = 0
start_time = time.time()
for key in urls:
    file_name = prefix + key
    print 'Processing ', file_name, ' ', format(count/37497.0, '.2f'), ' % done'
    s = Scrape(file_name, ['li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'p'])
    s.parse_content()
    tags = s.get_token_tags()
    tokens = s.get_token_frequencies()

    for token in tokens:
        record = index.find_one({'token': token})
        if record is None:
            document = {
                'token': token,
                'documents': [{
                    'file_name': file_name,
                    'count': tokens[token],
                    'tags': list(tags[token])
                }]
            }
            index.insert(document)
        else:
            document_info = {
                'file_name': file_name,
                'count': tokens[token],
                'tags': list(tags[token])
            }
            record['documents'].append(document_info)
            index.update({'token': token}, {"$set": record}, upsert=False)

print 'Time taken (seconds)\t:\t"', str((time.time() - start_time))


# token = 'apple'
# record = index.find_one({"token": token})
# if record is None:
#     index.insert({"token": token, "count": 0})
# else:
#     print record
#     record['count'] += 1
#     index.update({'token': token}, {"$set": record}, upsert=False)

