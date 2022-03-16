import requests
from requests_html import HTML
from bs4 import BeautifulSoup
import urllib
import re
from six import u

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

    # get artical link
    link = entry.select('.title a')[0].attrs['href']
    href = "https://www.ptt.cc{}".format(link)
    resp = fetchData(href)
    soup = BeautifulSoup(resp, 'html.parser')
    soup = soup.find(id="main-content")


    # get meta information (author, title, postTime)
    metaLine = soup.select('div.article-metaline')
    author = metaLine[0].text
    title = metaLine[1].text
    postTime = metaLine[2].text
    
    # remove meta nodes
    for meta in metaLine:
        meta.extract()
    for meta in soup.select('.article-metaline-right'):
        meta.extract()

    # remove and keep push nodes
    pushes = soup.find_all('div', class_='push')
    for push in pushes:
        push.extract()

    try:
        ip = soup.find(text=re.compile(u'※ 發信站:'))
        ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
    except:
        ip = "None"
    
    filtered = [ v for v in soup.stripped_strings if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--'] ]
    expr = re.compile(u(r'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/-_.?~%()]'))
    for i in range(len(filtered)):
        filtered[i] = re.sub(expr, '', filtered[i])

    filtered = [_f for _f in filtered if _f]  # remove empty strings
    filtered = [x for x in filtered if article_id not in x]  # remove last line containing the url of the article
    content = ' '.join(filtered)
    content = re.sub(r'(\s)+', ' ', content)
    print ('content:', content)

    meta = {
        'aid': aid,
        'title': title,
        'push': entry.select('.nrec')[0].text,
        'date': postTime,
        'author': author,
        'link': link,
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
            aid = str(pageIdx) + str(articleIdx).zfill(2)
            print(aid)
            meta = parseMeta(entry, aid)
            # if the article is deleted, then don't save it to list
            if meta == None:
                print("article was deleted")
            else:
                print(meta)
                pageData.append(meta)
    # csv header
    fieldnames = ['aid', 'title', 'push', 'date', 'author', 'link']
    with open('Gossiping_100.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # writer.writerow(pageData)
        for data in pageData:
            writer.writerow(data)
    
    print("end of the code")
