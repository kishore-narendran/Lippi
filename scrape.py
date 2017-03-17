from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from db import Term


class Scrape:
    def __init__(self, file_name, tags, remove_hyphen=None, remove_apostrophe=None, remove_stop_words=None):
        self.tags = tags
        with open(file_name, 'r') as file_handle:
            self.html = ''.join(file_handle.readlines())
            self.soup = BeautifulSoup(self.html, "html.parser")

        self.remove_hyphen = True if remove_hyphen is None else remove_hyphen
        self.remove_apostrophe = True if remove_apostrophe is None else remove_apostrophe
        self.remove_stop_words = True if remove_stop_words is None else remove_stop_words

        self.terms = []
        self.token_counter = 1

        self.stemmer = LancasterStemmer()

        self.doc_id = file_name.replace('WEBPAGES_RAW/', '')

    def parse_content(self, document):

        # Get a list of strings associated with each tag
        for x in self.soup.find_all(self.tags):
            tag = x.name
            if tag != 'p':
                tokens = self.tokenize(x.string)
            else:
                tokens = self.tokenize(x.text)
            if tokens is not None:
                for token in tokens:
                    # self.terms.append(Term(doc=document, term=token, tag_type=tag, position=self.token_counter))
                    self.terms.append({'doc': self.doc_id, 'term': token, 'tag_type': tag, 'position': self.token_counter})
                    self.token_counter += 1

        return self.terms

    def tokenize(self, text):

        # Checking if the text is a string value and is not None
        if text is None:
            return None

        # Convert to lowercase
        text = text.lower()

        # Removing hyphens and apostrophes if needed
        if self.remove_hyphen is True:
            text = text.replace('-', '')
        if self.remove_apostrophe is True:
            text = text.replace('\'', '')

        # Finding all the alphanumeric tokens and converting them to lowercase
        line_tokens = re.findall('\w+', text)

        # Uncomment the following line for stemming
        line_tokens = [self.stemmer.stem(token) for token in line_tokens]

        if self.remove_stop_words is True:
            line_tokens = filter(lambda token: token not in stopwords.words('english'), line_tokens)

        return line_tokens

