from pymongo import MongoClient
from nltk.corpus import stopwords
import re
from nltk.stem.lancaster import LancasterStemmer
from math import log
import json
import operator
import argparse


class Search:
    def __init__(self, search_query):
        self.search_query = search_query
        self.tokens = []
        self.tokens_stemmed = []
        self.stemmer = LancasterStemmer()

        # Creating a MongoClient and accessing the index collection
        self.client = MongoClient('mongodb://127.0.0.1:27017')
        self.db = self.client['cs222']
        self.index = self.db['terms']

        self.dcount = 37497.0

        self.tfidf = dict()

    def query_formulation(self):
        # Checking if the text is a string value and is not None
        if self.search_query is None:
            return

        # Removing hyphens and apostrophes if needed
        self.search_query = self.search_query.replace('-', '')
        self.search_query = self.search_query.replace('\'', '')

        # Finding all the alphanumeric tokens and converting them to lowercase
        self.tokens = re.findall('\w+', self.search_query)
        self.tokens = [token.lower() for token in self.tokens]
        self.tokens = [token for token in self.tokens if token not in stopwords.words('english')]

        # self.tokens_stemmed = set([self.stemmer.stem(token) for token in self.tokens])

    def get_document_tfidfs(self):
        for token in self.tokens:
            record = self.index.find_one({'token': token})
            documents = record['documents']
            # self.tfidf[token] = (list(), list())
            for document in documents:
                file_name = document['file_name'].replace('WEBPAGES_RAW/', '')
                if file_name in self.tfidf:
                    self.tfidf[file_name] += log(document['count'] + 1, 10) * log(self.dcount/len(documents), 10)
                else:
                    self.tfidf[file_name] = log(document['count'] + 1, 10) * log(self.dcount/len(documents), 10)
                # self.tfidf[token][0].append(document['file_name'].replace('WEBPAGES_RAW', ''))
                # temp_tfidf = log(document['count'] + 1, 10) * log(self.dcount/len(documents), 10)
                # self.tfidf[token][1].append(temp_tfidf)

    def get_results(self, number_of_results):
        prefix = 'WEBPAGES_RAW/'

        with open(prefix + 'bookkeeping.json', 'r') as file_handle:
            urls = json.load(file_handle)

        self.query_formulation()
        self.get_document_tfidfs()

        sorted_documents = sorted(self.tfidf.items(), key=operator.itemgetter(1))
        count = 1
        for document in sorted_documents:
            print "Result\t", count, " - ", urls[document[0]], ' (', document[0], ')'

            if count == number_of_results:
                break

            count += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ICS UCI Search Engine')
    parser.add_argument('-s', '--search', required=True, help='Search query')
    parser.add_argument('-n', '--number', required=False, help='Number of results')

    args = parser.parse_args()

    s = Search(args.search)
    if args.number is not None:
        s.get_results(int(args.number))
    else:
        s.get_results(10)











