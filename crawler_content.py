import csv
from bs4 import BeautifulSoup
from crawler_artical import fetchData

def crawlerComment(soup, aid):
  commentList = list()
  comments = soup.find_all('div', 'push')       # find all the comments
  for comment in comments:
    meta = {
      'aid': aid,
      'userid': comment.find('span', 'f3 hl push-userid').getText().replace(':', '').strip(),
      'message': comment.find('span', 'f3 push-content').getText().replace(':', '').strip(),
    }
    print(meta)
    commentList.append(meta)
  return commentList

def saveCSV(commentsList):
  fieldnames = ['aid', 'userid', 'message']
  with open('Gossiping_100_comments.csv', 'w', encoding='UTF8', newline='') as f:  
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for comments in commentsList:
      for comment in comments:
        writer.writerow(comment)

with open('./Gossiping_100.csv', newline='') as csvfile:
  rows = csv.DictReader(csvfile)
  commentsList = list()

  # 以迴圈輸出指定欄位
  for row in rows:
    href = "https://www.ptt.cc{}".format(row["link"])
    print(href)
    aid = row['aid']
    resp = fetchData(href)
    soup = BeautifulSoup(resp, 'html.parser')
    metaLine = soup.select('.article-metaline .article-meta-value')
    
    author = metaLine[0].text
    artical = metaLine[1].text
    postTime = metaLine[2].text

    comments = crawlerComment(soup, aid)
    commentsList.append(comments)

  saveCSV(commentsList)
