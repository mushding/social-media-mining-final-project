import requests
from requests_html import HTML
import urllib
import re

def fetchData(url):
    '''
    Step 1. 
    Get the Gossiping with pass through the 18-year-old page
    '''
    resp = requests.get(url, cookies={'over18': '1'})  # 一直向 server 回答滿 18 歲了 !
    return resp.text

def parseArtical(html):
    '''
    Step 2.
    Get artical list, which contains every artical in the page
    '''
    post_entries = html.find('div.r-ent')
    return post_entries


def parseMeta(entry):
    '''
    Step 3.
    Get every meta in entry, and return dict
    '''
    meta = {
        'title': entry.find('div.title', first=True).text,
        'push': entry.find('div.nrec', first=True).text,
        'date': entry.find('div.date', first=True).text,
    }

    try:
        # 正常狀況取得資料
        meta['author'] = entry.find('div.author', first=True).text
        meta['link'] = entry.find('div.title > a', first=True).attrs['href']
    except AttributeError:
        # 但碰上文章被刪除時，就沒有辦法像原本的方法取得 作者 跟 連結
        if '(本文已被刪除)' in meta['title']:
            # e.g., "(本文已被刪除) [haudai]"
            match_author = re.search('\[(\w*)\]', meta['title'])
            if match_author:
                meta['author'] = match_author.group(1)
        elif re.search('已被\w*刪除', meta['title']):
            # e.g., "(已被cappa刪除) <edisonchu> op"
            match_author = re.search('\<(\w*)\>', meta['title'])
            if match_author:
                meta['author'] = match_author.group(1)
    # 最終仍回傳統一的 dict() 形式 paired data
    return meta


if __name__ == '__main__':
    pageNum = 100
    pageData = list()

    # Step 1. get Gossiping Data pass through over-18
    url = "https://www.ptt.cc/bbs/Gossiping/index.html"
    resp = fetchData(url)

    # convert rawData to HTML
    initHTML = HTML(html=resp)

    # next page
    btns = initHTML.find('.action-bar a.btn.wide')
    prevPageBtn = btns[1].attrs['href']

    # get prevPage index
    prevPageIdx = int(prevPageBtn.split('/')[3].replace('index', '').split('.')[0])

    for idx in range(prevPageIdx - pageNum, prevPageIdx + 1): # /bbs/Gossiping/index3424.html
        page_url = urllib.parse.urljoin('https://www.ptt.cc/bbs/Gossiping/', 'index' + str(idx) + ".html")

        # step 2. parse Data to Artical list
        resp = fetchData(page_url)
        pageHTML = HTML(html=resp)
        post_entries = parseArtical(pageHTML)  # step-2

        # one page
        for entry in post_entries:
            pageData.append(parseMeta(entry))   # setp-3

        print(pageData)

    