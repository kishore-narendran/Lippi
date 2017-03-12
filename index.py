from scrape import Scrape
from pymongo import MongoClient
import json
import time


class Index:
    def __init__(self):
        self.index = dict()

    def update_index(self, token, file_name, count, tags):
        # Updating the list of documents if the token is already present in the index
        if token in self.index:
            self.index[token].append({
                'file_name': file_name,
                'count': count,
                'tags': tags
            })
        # Creating a new entry for the token
        else:
            self.index[token] = [{
                    'file_name': file_name,
                    'count': count,
                    'tags': tags
            }]

    def write_to_mongo(self):
        # Creating a MongoClient and accessing the index collection
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['cs222']
        index = db['index']

        # Writing each token and the associated documents into the mongoDB collection
        for token in self.index:
            index.insert({
                'token': token,
                'documents': self.index[token]
            })


def scrape_and_index():
    prefix = 'WEBPAGES_RAW/'

    with open(prefix + 'bookkeeping.json', 'r') as file_handle:
        urls = json.load(file_handle)

    index = Index()

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
            index.update_index(token, key, tokens[token], list(tags[token]))

        count += 1

        if count == 100:
            break

    print 'Time taken (seconds)\t:\t"', str((time.time() - start_time))

    index.write_to_mongo()

if __name__ == '__main__':
    scrape_and_index()


# token = 'apple'
# record = index.find_one({"token": token})
# if record is None:
#     index.insert({"token": token, "count": 0})
# else:
#     print record
#     record['count'] += 1
#     index.update({'token': token}, {"$set": record}, upsert=False)

