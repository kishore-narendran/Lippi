import tfidf
from collections import Counter
import json
import time
import argparse
import re
from termcolor import colored
from bs4 import BeautifulSoup

def find_documents(term):
    start_time = time.time()
    x = tfidf.terms_collection.distinct('doc', {'term': term})
    print "Find Documents Time = ", str((time.time() - start_time))
    return x


def compute_document_score_by_term(term, tags=None):
    # documents = find_documents(term)
    scores = tfidf.tf_idf(term, tags)
    # start_time = time.time()
    # res = tfidf.terms_collection.aggregate([
    #     {'$match': {'term': term}},
    #     {
    #         '$group': {
    #             '_id': "$doc",
    #             'count': {'$sum': 1}
    #         }
    #     }
    # ])
    # for doc in res:
    #     scores[doc['_id']] = tfidf.tf_idf(term, doc['_id'], doc['count'])
    # print "Find Score Time = ", str((time.time() - start_time))

    # for doc in documents:
    #     scores[doc] = tfidf.tf_idf(term, doc)
    return scores


def compute_document_score_query(query_terms):
    scores = Counter()

    with open('WEBPAGES_RAW/bookkeeping.json') as file_handle:
        urls = json.load(file_handle)

    for term in query_terms:
        term_scores = compute_document_score_by_term(term)

        # query_term_weight = log((1 + tfidf.NUMBER_OF_DOCUMENTS/float(tfidf.find_document_frequency(term))), 10)
        # print query_term_weight

        # for doc in term_scores.keys():
        #     term_scores[doc] = query_term_weight * term_scores[doc]
        # term_scores = Counter({doc: (query_term_weight * term_scores[doc]) for doc in term_scores})
        # print term, len(term_scores)
        # print term_scores

        for doc in term_scores:
            scores[doc] += term_scores[doc]

    final_results = scores.most_common(10)
    return [urls[x] for x, y in final_results]


def find_results(query_terms, page_rank_factor, factors=None, n_results=5):
    scores = Counter()

    with open('page_rank.json') as file_handle:
        page_ranks = json.load(file_handle)

    with open('WEBPAGES_RAW/bookkeeping.json') as file_handle:
        urls = json.load(file_handle)

    min_page_rank = min(page_ranks.values())
    max_page_rank = max(page_ranks.values())

    page_ranks = {doc: ((page_ranks[doc] - min_page_rank)**2 / float(max_page_rank - min_page_rank)**2)
                  for doc in page_ranks}

    all_docs = None
    union_docs = set()
    for term in query_terms:
        if factors is None:
            term_scores = compute_document_score_by_term(term)
            term_docs = set()
            for doc in term_scores:
                scores[doc] += term_scores[doc]
                term_docs.add(doc)

            if all_docs is None:
                all_docs = term_docs
            else:
                all_docs = all_docs.intersection(term_docs)

        else:
            term_scores_title = compute_document_score_by_term(term, ['title'])
            term_scores_h = compute_document_score_by_term(term, ['a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            term_scores_all = compute_document_score_by_term(term, ['p'])

            term_docs = set()
            for doc in term_scores_title:
                scores[doc] += factors[0] * term_scores_title[doc]
                term_docs.add(doc)

            for doc in term_scores_h:
                scores[doc] += factors[1] * term_scores_h[doc]
                term_docs.add(doc)

            for doc in term_scores_all:
                scores[doc] += factors[2] * term_scores_all[doc]
                term_docs.add(doc)

            if all_docs is None:
                all_docs = term_docs
            else:
                all_docs = all_docs.intersection(term_docs)

            union_docs.union(term_docs)

    for doc in scores:
        scores[doc] += page_rank_factor * (0 if doc not in page_ranks else page_ranks[doc])

    final_doc_scores = Counter()
    for doc in all_docs:
        final_doc_scores[doc] = scores[doc]

    if len(final_doc_scores) < n_results:
        union_docs_scores = Counter()
        for doc in union_docs:
            if doc not in final_doc_scores:
                union_docs_scores[doc] = scores[doc]
        final_results = final_doc_scores.most_common(len(final_doc_scores))
        union_results = union_docs_scores.most_common(n_results - len(final_doc_scores))
        if union_results is not None:
            final_results.extend(union_results)
    else:
        final_results = final_doc_scores.most_common(n_results)

    # print final_results
    return [x for x, y in final_results], [urls[x] for x, y in final_results]


def print_results(docs, query_tokens):
    if len(docs) == 0:
        print 'No results found!'
        return

    with open('WEBPAGES_RAW/bookkeeping.json') as file_handle:
        urls = json.load(file_handle)

    count = 1
    for doc in docs:
        url = colored(urls[doc], 'green', attrs=['bold'])
        count_text = colored(str(count), 'cyan', attrs=['bold'])
        print count_text, url

        with open('WEBPAGES_RAW/' + doc, 'r') as file_handle:
            html = ''.join(file_handle.readlines())
            soup = BeautifulSoup(html, "html.parser")

        title = soup.find('title')
        if title is not None:
            title = title.string.strip()
            title = colored(title, 'yellow')
            print title
        else:
            print 'No Title'

        for query_token in query_tokens:
            def predicate(e):
                return e and e.name != u'title' and query_token in e.text.lower()

            try:
                text = soup.find_all(predicate)[0].text
                text_lower = text.lower().split()
                text = text.split()
                text_pos = text_lower.index(query_token)
                begin_index = max(0, text_pos - 10)
                end_index = min(text_pos + 10, len(text))
                text = text[begin_index:end_index]
                for token in text:
                    if token.lower() in query_tokens:
                        print colored(token, 'white', attrs=['bold']),
                    else:
                        print token,
                print '...'
                break
            except IndexError:
                pass
            except ValueError:
                pass

        print
        count += 1


def process_query_string(query, remove_hyphen=True, remove_apostrophe=True):
    # Convert to lowercase
    text = query.lower()

    # Removing hyphens and apostrophes if needed
    if remove_hyphen is True:
        text = text.replace('-', '')
    if remove_apostrophe is True:
        text = text.replace('\'', '')

    # Finding all the alphanumeric tokens and converting them to lowercase
    line_tokens = re.findall('\w+', text)

    return line_tokens


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ICS UCI Search Engine')
    parser.add_argument('-s', '--search', required=True, help='Search query')
    parser.add_argument('-n', '--number', required=False, help='Number of results')

    args = parser.parse_args()

    query_tokens = process_query_string(args.search)

    if args.number is not None:
        docs, results = find_results(query_tokens, 100, (0.8, 0.0, 0.2), args.number)
    else:
        docs, results = find_results(query_tokens, 100, (0.8, 0.0, 0.2), 5)

    print_results(docs, query_tokens)
