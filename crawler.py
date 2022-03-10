import requests
from requests_html import HTML

def fetchData(url):
    '''
    Step 1. 
    Get the Gossiping with pass through the 18-year-old page
    '''
    resp = requests.get(url, cookies={'over18': '1'})  # 一直向 server 回答滿 18 歲了 !
    return resp.text

def parseArtical(doc):
    '''
    Step 2.
    Get artical list, which contains every artical in the page
    '''
    html = HTML(html=doc)
    post_entries = html.find('div.r-ent')
    return post_entries


def parseMeta(entry):
    '''
    Step 3.
    Get every meta in entry, and return dict
    '''
    return {
        'title': entry.find('div.title', first=True).text,
        'push': entry.find('div.nrec', first=True).text,
        'date': entry.find('div.date', first=True).text,
        'author': entry.find('div.author', first=True).text,
        'link': entry.find('div.title > a', first=True).attrs['href'],
    }

if __name__ == '__main__':
    url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    resp = fetchData(url)  # step-1
    post_entries = parseArtical(resp.text)  # step-2

    for entry in post_entries:
        meta = parseMeta(entry)  # setp-3

