import numpy as np
from google_search import get_google_results
from query import find_results
import json


def mean_reciprocal_rank(q, o):
    rs = []
    for j in range(len(q)):
        temp = []
        flag = 0
        for i in range(len(q[j])):
            if q[j][i] in o[j] and (flag == 0):
                temp.append(1)
                flag = 1
            else:
                temp.append(0)
        rs.append(temp)
    print rs
    rs = (np.asarray(r).nonzero()[0] for r in rs)
    return np.mean([1. / (r[0] + 1) if r.size else 0. for r in rs])


def r_precision(r):
    r = np.asarray(r) != 0
    z = r.nonzero()[0]
    if not z.size:
        return 0.
    return np.mean(r[:z[-1] + 1])


def precision_at_k(r, k):
    assert k >= 1
    r = np.asarray(r)[:k] != 0
    if r.size != k:
        raise ValueError('Relevance score length < k')
    return np.mean(r)


def average_precision(q, o):
    rs = []
    for j in range(len(q)):
        temp = []
        for i in range(len(q[j])):
            if q[j][i] in o[j]:
                first = i
                temp.append(1)
            else:
                temp.append(0)
        rs.append(temp)
    meanscore = []
    for r in rs:
        r = np.asarray(r) != 0
        out = [precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
        if not out:
            return 0.
        meanscore.append(np.mean(out))
    return np.mean(np.array(meanscore))


def dcg_at_k(r, k, method=0):
    r = np.asfarray(r)[:k]
    if r.size:
        if method == 0:
            return r[0] + np.sum(r[1:] / np.log2(np.arange(2, r.size + 1)))
        elif method == 1:
            return np.sum(r / np.log2(np.arange(2, r.size + 2)))
        else:
            raise ValueError('method must be 0 or 1.')
    return 0.


def ndcg_at_k(q, o, k, method=0):
    rs = []
    for j in range(len(q)):
        temp = []
        for i in range(len(q[j])):
            if q[j][i] in o[j]:
                temp.append(k - o[j].index(q[j][i]))
            else:
                temp.append(0)
        rs.append(temp)
    meanscore = []
    for r in rs:
        dcg_max = dcg_at_k(sorted(r, reverse=True), k, method)

        if not dcg_max:
            meanscore.append(0.0)
        else:
            meanscore.append(dcg_at_k(r, k, method) / dcg_max)

    return np.mean(np.array(meanscore))


if __name__ == "__main__":
    # queryRes=[["a","c","z","e"],["b","c","d"],["a","d","e"]]
    # Oracle=[["c","a","e", "z"],["e","b","c"],["d","e","f"]]
    # #Takes a list of query responses and list of oracle responses
    # print mean_reciprocal_rank(queryRes,Oracle)
    # print ndcg_at_k(queryRes,Oracle,3, method=0)
    # print average_precision(queryRes,Oracle)

    queries = ["mondego", "machine learning", "software engineering", "security", "student affairs", "graduate courses",
               "Crista Lopes", "REST", "computer games", "information retrieval"]

    # queries = ["mondego", "crista lopes"]

    # google_results = get_google_results(queries)
    google_results = [[u'mondego.ics.uci.edu', u'networkdata.ics.uci.edu/netdata/html/Mondego.html',
                       u'mondego.ics.uci.edu/projects/clonedetection', u'www.ics.uci.edu/~lopes',
                       u'www.ics.uci.edu/~lopes/teaching/cs221W12'],
                      [u'archive.ics.uci.edu/ml', u'archive.ics.uci.edu/ml/datasets.html', u'cml.ics.uci.edu',
                       u'cml.ics.uci.edu/2016/03/southern-california-machine-learning-symposium',
                       u'archive.ics.uci.edu/ml/machine-learning-databases'],
                      [u'www.ics.uci.edu/prospective/en/degrees/software-engineering',
                       u'www.ics.uci.edu/ugrad/degrees/degree_se.php', u'www.ics.uci.edu/prospective/pdf/se.pdf',
                       u'www.ics.uci.edu/faculty/area/area_software.php',
                       u'www.ics.uci.edu/~djr/DebraJRichardson/SE4S.html'],
                      [u'www.ics.uci.edu/faculty/area/area_security.php', u'sconce.ics.uci.edu/134-S11/LEC3.pdf',
                       u'sprout.ics.uci.edu', u'www.ics.uci.edu/computing/linux/security.php',
                       u'sprout.ics.uci.edu/past_projects/odb'],
                      [u'www.ics.uci.edu/grad/sao', u'www.ics.uci.edu/prospective/en/contact/student-affairs',
                       u'www.ics.uci.edu/about/search/search_sao.php', u'www.ics.uci.edu/ugrad',
                       u'www.ics.uci.edu/grad'],
                      [u'www.ics.uci.edu/grad/courses', u'www.ics.uci.edu/grad/degrees/degree_inf-sw.php',
                       u'www.ics.uci.edu/grad/policies/GradPolicies_Grading.php',
                       u'www.ics.uci.edu/grad/courses/details.php?id=16',
                       u'www.ics.uci.edu/grad/courses/details.php?id=521'],
                      [u'www.ics.uci.edu/~lopes', u'www.ics.uci.edu/~lopes/teaching/cs221W12',
                       u'www.ics.uci.edu/~lopes/teaching/inf102S14', u'www.ics.uci.edu/~lopes/teaching/inf212W12',
                       u'www.ics.uci.edu/~lopes/patents.html'],
                      [u'www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm',
                       u'www.ics.uci.edu/~fielding/pubs/dissertation/top.htm',
                       u'www.ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf',
                       u'www.ics.uci.edu/~fielding/pubs/dissertation/introduction.htm',
                       u'www.ics.uci.edu/~tdebeauv/swarch/INF123-11-REST.pptx'],
                      [u'cgvw.ics.uci.edu', u'www.ics.uci.edu/prospective/en/degrees/computer-game-science',
                       u'www.ics.uci.edu/ugrad/degrees/degree_cgs.php', u'cgvw.ics.uci.edu/author/venita',
                       u'cgvw.ics.uci.edu/tag/virtual-worlds'],
                      [u'www.ics.uci.edu/~lopes/teaching/cs221W15', u'www.ics.uci.edu/~lopes/teaching/cs221W13',
                       u'www.ics.uci.edu/~welling/publications/papers/GenHarm3.pdf',
                       u'www.ics.uci.edu/~djp3/classes/2009_01_02_INF141/calendar.html',
                       u'www.ics.uci.edu/~rnuray/pubs/ipm2006.pdf']]
    # print google_results, len(google_results[0])

    prefix = 'WEBPAGES_RAW/'
    with open(prefix + 'bookkeeping.json', 'r') as file_handle:
        urls = json.load(file_handle)

    # pr_factor_list = [10, 20, 40, 50, 75, 100, 125, 150, 200, 250]
    # title_factor_list = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # header_factor_list = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]

    pr_factor_list = [10]
    title_factor_list = [0.8]
    header_factor_list = [0.0]


    scores = []
    for pr_factor in pr_factor_list:
        for title_factor in title_factor_list:
            for header_factor in header_factor_list:
                if title_factor + header_factor > 1.0:
                    continue
                else:
                    test_results = []
                    p_factor = 1.0 - title_factor - header_factor
                    for query in queries:
                        query_results = find_results(query.lower().split(), pr_factor,
                                                     (title_factor, header_factor, p_factor))
                        test_results.append(query_results[1])

                    # print test_results
                    score = ndcg_at_k(test_results, google_results, 5, method=0)
                    ap = mean_reciprocal_rank(test_results, google_results)
                    scores.append(((pr_factor, title_factor, header_factor, p_factor), score))
                    print ((pr_factor, title_factor, header_factor, p_factor), score, ap)

    print "\nRESULTS"
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    print sorted_scores[:10]
