import requests
from requests_html import HTML
import urllib
import re

import csv

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


def parseMeta(entry, idx):
    '''
    Step 3.
    Get every meta in entry, and return dict
    '''
    meta = {
        'aid': idx,
        'title': entry.find('div.title', first=True).text,
        'push': entry.find('div.nrec', first=True).text,
        'date': entry.find('div.date', first=True).text,
    }

    try:
        # 正常狀況取得資料
        meta['author'] = entry.find('div.author', first=True).text
        meta['link'] = entry.find('div.title > a', first=True).attrs['href']
    except AttributeError:
        return 
        
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
        print(idx)
        # step 2. parse Data to Artical list
        resp = fetchData(page_url)
        pageHTML = HTML(html=resp)
        post_entries = parseArtical(pageHTML)  # step-2

        # one page
        for entry in enumerate(post_entries):
            pageData.append(parseMeta(entry, idx))   # setp-3

    # csv header
    fieldnames = ['aid', 'title', 'push', 'date', 'author', 'link']
    with open('Gossiping_100.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pageData)