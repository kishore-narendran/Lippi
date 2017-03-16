from bs4 import BeautifulSoup
import re
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer


class Scrape:
    def __init__(self, file_name, tags, remove_hyphen=None, remove_apostrophe=None, remove_stop_words=None):
        self.tags = tags
        with open(file_name, 'r') as file_handle:
            self.html = ''.join(file_handle.readlines())
            self.soup = BeautifulSoup(self.html, "html.parser")

        self.remove_hyphen = True if remove_hyphen is None else remove_hyphen
        self.remove_apostrophe = True if remove_apostrophe is None else remove_apostrophe
        self.remove_stop_words = True if remove_stop_words is None else remove_stop_words

        self.token_counts = defaultdict(int)
        self.token_tag = dict()

        self.stemmer = LancasterStemmer()

    def parse_content(self):
        content = {tag: [] for tag in self.tags}

        # Get a list of strings associated with each tag
        for x in self.soup.find_all(self.tags):
            tag = x.name
            if tag != 'p':
                self.tokenize(x.string, tag)
                content[tag].append(x.string)
            else:
                self.tokenize(x.text, tag)
                content[tag].append(x.text)

        return content

    def update_counts(self, tokens, tag):
        # Updating the token counts, and the tag in which the tokens were found
        for token in tokens:
            self.token_counts[token] += 1

            if token in self.token_tag:
                self.token_tag[token].add(tag)
            else:
                self.token_tag[token] = set([tag])

    def tokenize(self, text, tag):

        # Checking if the text is a string value and is not None
        if text is None:
            return

        # Convert to lowercase
        text = text.lower()

        # Removing hyphens and apostrophes if needed
        if self.remove_hyphen is True:
            text = text.replace('-', '')
        if self.remove_apostrophe is True:
            text = text.replace('\'', '')

        # Finding all the alphanumeric tokens and converting them to lowercase
        line_tokens = re.findall('\w+', text)
        # line_tokens = [self.stemmer.stem(token.lower()) for token in line_tokens]

        if self.remove_stop_words is True:
            line_tokens = filter(lambda token: token not in stopwords.words('english'), line_tokens)
            #line_tokens = [token for token in line_tokens if token not in stopwords.words('english')]

        self.update_counts(line_tokens, tag)

        return line_tokens

    def get_token_frequencies(self):
        return self.token_counts

    def get_token_tags(self):
        return self.token_tag

