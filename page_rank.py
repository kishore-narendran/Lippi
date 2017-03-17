from bs4 import BeautifulSoup
import re
import json
import urlparse
import networkx as nx

PREFIX = 'WEBPAGES_RAW/'
urls_set = set([])

def generate_graph():
    adjacency = {}

    with open(PREFIX + 'reverse_bookkeeping.json', 'r') as file_handle:
        urls = json.load(file_handle)

    urls_set = set(urls.keys())

    for url in urls:
        file_name = PREFIX + urls[url]

        with open(file_name, 'r') as file_handle:
            html = ''.join(file_handle.readlines())
            soup = BeautifulSoup(html, "html.parser")

            links = []
            for item in soup.find_all('a'):
                try:
                    outgoing_link = item['href']
                    links.append(outgoing_link)
                except:
                    continue

            links = set(map(lambda x: urlparse.urljoin("http://" + url, x)[7:], links))
            links = list(links.intersection(urls_set))
            adjacency[url] = links

    return adjacency


def read_graph_doc_id():
    with open('graph.json') as file_handle:
        graph = json.load(file_handle)
    return graph

if __name__ == "__main__":
    # graph = generate_graph()
    # json.dump(graph, open("graph.json", 'w'))

    graph = read_graph_doc_id()
    G = nx.DiGraph()
    G.add_nodes_from(graph.keys())

    for key in graph.keys():
        for item in graph[key]:
            G.add_edge(key, item)

    rank = nx.pagerank(G, alpha=0.95)
    rank_out = open('page_rank.json', 'w')
    json.dump(rank, rank_out)

    # Print key with maximum value
    import operator

    sorted_rank = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)
    print "Max ranks: ", sorted_rank[:10]