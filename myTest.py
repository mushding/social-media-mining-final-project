import requests
from requests_html import HTML
from bs4 import BeautifulSoup
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
    html = HTML(html=html)
    post_entries = html.find('div.r-ent')
    return post_entries

def parseMeta(entry, aid):
    '''
    Step 3.
    Get every meta in entry, and return dict
    '''
    if "(本文已被刪除)" in entry.select('.title')[0].text:
        return
    elif re.search("已被\w*刪除", entry.select('.title')[0].text):
        return
    
    meta = {
        'aid': aid,
        'title': entry.select('.title')[0].text.split('\n')[1],
        'push': entry.select('.nrec')[0].text,
        'date': entry.select('.date')[0].text,
        'author': entry.select('.author')[0].text,
        'link': entry.select('.title a')[0].attrs['href'],
    }
    return meta

if __name__ == "__main__":
    pageData = list()
    pageNum = 100

    # Step 1. get Gossiping Data pass through over-18
    url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    resp = fetchData(url)

    # convert rawData to HTML
    initHTML = HTML(html=resp)

    # next page
    btns = initHTML.find('.action-bar a.btn.wide')
    prevPageBtn = btns[1].attrs['href']

    # get prevPage index
    prevPageIdx = int(prevPageBtn.split('/')[3].replace('index', '').split('.')[0])

    for pageIdx in range(prevPageIdx - pageNum, prevPageIdx + 1):
        page_url = urllib.parse.urljoin('https://www.ptt.cc/bbs/Gossiping/', 'index' + str(pageIdx) + ".html")
        print(pageIdx)
        resp = fetchData(page_url)
        soup = BeautifulSoup(resp, 'html.parser')
        # Step 2. get the article block
        post_entries = soup.select('.r-ent')
        for articleIdx, entry in enumerate(post_entries):
            aid = str(pageIdx) + str(articleIdx)
            print(aid)
            meta = parseMeta(entry, aid)
            # if the article is deleted, then don't save it to list
            if meta == None:
                print("article was deleted")
            else:
                pageData.append(meta)
    # csv header
    fieldnames = ['aid', 'title', 'push', 'date', 'author', 'link']
    with open('Gossiping_test.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # writer.writerow(pageData)
        for data in pageData:
            writer.writerow(data)
    
    print("end of the code")
