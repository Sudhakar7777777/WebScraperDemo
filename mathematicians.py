from scraper import simple_get, json_get
from scraper import log_error
from urllib import parse
from bs4 import BeautifulSoup
from datetime import date
import json


def get_names():
    """
        Downloads the page where the list of mathematicians is found
        and returns a list of strings, one per mathematician
    """
    url = 'http://www.fabpedigree.com/james/mathmen.htm'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        names = set()
        for li in html.select('li'):
            for name in li.text.split('\n'):
                if len(name) > 0:
                    names.add(name.strip())
        return list(names)

    # Raise an exception if we failed to get any data from the url
    raise Exception('Error retrieving contents at {}'.format(url))


def get_hits_on_name(name):
    """
        Accepts a `name` of a mathematician and returns the number
        of hits that mathematician's Wikipedia page received in the
        last 60 days, as an `int`
    """
    # Read documentation : https://wikimedia.org/api/rest_v1/#/
    # curl -X GET "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/
    #               all-agents/Srinivasa%20Ramanujan/monthly/19000101/20190901" -H "accept: application/json"
    # url_root is a template string that is used to build a URL.
    url_root = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/' \
               'all-agents/{NAME}/monthly/{START}/{END}'
    start = '20000101'
    today = date.today().strftime("%Y%m%d")
    encoded_name = parse.quote(name)
    url = url_root.replace('{NAME}', encoded_name, 1).replace('{START}', start, 1).replace('{END}', today, 1)
    print(url)
    response = json_get(url)
    print(response)
    if response is not None:
        json_resp = json.loads(response)
        total = 0
        for item in json_resp['items']:
            total = total + item['views']
        print(total)
    return total


if __name__ == '__main__':
    print('Getting the list of names....')
    names = get_names()
    print('... done.\n')

    results = []
    print('Getting stats for each name....')

    # name = names.pop()
    # get_hits_on_name(name)
    for name in names:
        try:
            hits = get_hits_on_name(name)
            if hits is None:
                hits = -1
            results.append((hits, name))
            exit(0)
        except:
            results.append((-1, name))
            log_error('error encountered while processing '
                      '{}, skipping'.format(name))
    print('... done.\n')

    results.sort()
    results.reverse()

    if len(results) > 5:
        top_marks = results[:5]
    else:
        top_marks = results

    print('\nThe most popular mathematicians are:\n')
    for (mark, mathematician) in top_marks:
        print('{} with {} pageviews'.format(mathematician, mark))

    no_results = len([res for res in results if res[0] == -1])
    print('\nBut we did not find results for '
          '{} mathematicians on the list'.format(no_results))