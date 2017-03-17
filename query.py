import tfidf
from collections import Counter
import json
import time


def find_documents(term):
    start_time = time.time()
    x = tfidf.terms_collection.distinct('doc', {'term': term})
    print "Find Documents Time = ", str((time.time() - start_time))
    return x


def compute_document_score_by_term(term):
    # documents = find_documents(term)
    scores = tfidf.tf_idf(term)
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

    return scores.most_common(5)


def find_results(query_terms):
    scores = Counter()
    all_term_scores = []
    document_set = None
    with open('page_rank.json') as file_handle:
        page_ranks = json.load(file_handle)

    with open('WEBPAGES_RAW/bookkeeping.json') as file_handle:
        urls = json.load(file_handle)

    min_page_rank = min(page_ranks.values())
    max_page_rank = max(page_ranks.values())

    page_ranks = {doc: ((page_ranks[doc] - min_page_rank)/float(max_page_rank-min_page_rank)) for doc in page_ranks}

    final_results = []
    single_term_results = []
    for term in query_terms:
        term_scores = compute_document_score_by_term(term)

        max_term_score = max(term_scores.values())
        min_term_scores = min(term_scores.values())

        term_scores = Counter({doc: ((term_scores[doc] - min_term_scores) / float(max_term_score - min_term_scores))
                               for doc in term_scores})

        temp_term_scores = Counter({doc:(0.50 * term_scores[doc] +
                                         0.50 * (0.0 if doc not in page_ranks else page_ranks[doc])) for doc in term_scores})
        top_term_result = temp_term_scores.most_common(1)
        print top_term_result[0]
        # del term_scores[top_term_result[0]]

        single_term_results.extend(top_term_result)

        all_term_scores.append(term_scores)

        if document_set is None:
            document_set = set(term_scores.keys())
        else:
            document_set.intersection(set(term_scores.keys()))

    # final_results = list(set(sorted(single_term_results, key=lambda tup: tup[1], reverse=True)))
    final_results = []

    for doc in document_set:
        scores[doc] = 0.0
        for term_score in all_term_scores:
            scores[doc] += term_score[doc]
        scores[doc] /= len(all_term_scores)
        scores[doc] = 0.50 * scores[doc] + 0.50 * (0.0 if doc not in page_ranks else page_ranks[doc])
    final_results.extend(scores.most_common(5))

    final_results = sorted(final_results, key=lambda tup: tup[1], reverse=True)

    return [urls[x] for x,y in final_results]


if __name__ == "__main__":
    print find_results(['crista', 'lopes'])
