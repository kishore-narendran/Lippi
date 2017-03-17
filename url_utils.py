import json

def findPrevSlash(url, dot_index):
    index = url[:dot_index-1].rfind("/")
    return index

def resolve_dots(url):
    dot_index = url.find('..')
    while (dot_index!=-1):
        prevSlashIndex = findPrevSlash(url, dot_index)
        url = url[:prevSlashIndex] + url[dot_index+2:]
        dot_index = url.find('..')
    return url


def create_pagerank_bookkeeping(bookkeeping_filepath, reverse_book_filepath):
    with open(bookkeeping_filepath, 'r') as file_handle:
        urls = json.load(file_handle)

    reverse_book = {}

    for doc in urls:
        resolved_url = resolve_dots(urls[doc])
        reverse_book[resolved_url] = doc

    f = open(reverse_book_filepath, 'w')
    json.dump(reverse_book, f)

if __name__=="__main__":
    PREFIX = PREFIX = 'WEBPAGES_RAW/'
    create_pagerank_bookkeeping(PREFIX + 'bookkeeping.json', PREFIX + 'reverse_bookkeeping.json')