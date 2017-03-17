from google import search

def get_google_results(queries):
    results = []
    for query in queries:
        result = list(search('site:ics.uci.edu '+'"'+query+'"',tld='com', lang='en', stop=5))
        result = map(lambda x: x[x.find("//")+2:], result)
        result = map(lambda x: x[:-1] if x.endswith("/") else x, result)

        results.append(result)



    return results