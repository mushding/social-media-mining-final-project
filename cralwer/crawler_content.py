from cmath import exp
import pandas as pd
import csv
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup
from crawler_artical import fetchData
from tqdm import tqdm, trange

# 爬 comment 資料
def crawlerComment(soup, aid):
    commentList = list()
    meta = {}
    comments = soup.find_all('div', 'push')             # find all the comments
    
    for comment in comments:
        # "推" is 'hl push-tag', "噓" is 'f1 hl push-tag'
        try:
            if (comment.find('span', 'hl push-tag')):
                tag = comment.find('span', 'hl push-tag').getText().strip()
            else:
                tag = comment.find('span', 'f1 hl push-tag').getText().strip()
        except Exception:
            print(Exception)

        try:
            userid = comment.find('span', 'f3 hl push-userid').getText()
            message = comment.find('span', 'f3 push-content').getText().replace(':', '').strip()
            metaLine = comment.find('span', 'push-ipdatetime').getText().strip().split()
        except Exception:
            print(Exception)
        
        if (len(metaLine) == 2):
            ip = ""
            time = metaLine[0] + " " + metaLine[1]
        elif (len(metaLine) == 3):
            ip = metaLine[0]
            time = metaLine[1] + " " + metaLine[2]
        else:
            ip = ""
            time = ""

        meta = {
            'aid': aid,
            'tag': tag,
            'userid': userid,
            'message': message,
            'ip': ip,
            'time': time,
        }
        commentList.append(meta)

    return commentList

# 找 article csv 的 LastRowNum
def findLastRowNum(path, articleDF):
    with open(path, newline='') as csvfile:
        comment = csv.DictReader(csvfile)
        commentList = list(comment)
        lastRowNum = 0

        if (len(commentList) == 0):                             # no data in commentList
            pass
        else:
            comment_last_aid = int(commentList[-1]['aid'])      # 取得 comments.csv 的最後一個 aid
            lastRowNum = list(articleDF['aid']).index(comment_last_aid) + 1

        return lastRowNum

# 新增新的 comment 到現有的 csv
def appendListToCSV(path, commentsList):
    fieldnames = ['aid', 'tag', 'userid', 'message', 'ip', 'time']
    with open(path, 'a+', newline='') as f:
        dictWriter = csv.DictWriter(f, fieldnames=fieldnames)
        dictWriter.writerows(commentsList)


if __name__ == "__main__":
    Gossiping_path = "../data/cralwer/Gossiping_20000.csv"
    Gossiping_comments_path = "../data/cralwer/Gossiping_20000_comments.csv"

    articleDF = pd.read_csv(Gossiping_path)
    articleLen = len(articleDF)
    lastRowNum = 0

    if (not Path(Gossiping_comments_path).exists()):         # if comments.csv doesn't exist
        # create a new .csv file
        fieldnames = ['aid', 'tag', 'userid', 'message', 'ip', 'time']
        with open(Gossiping_comments_path, 'w', encoding='UTF8', newline='') as f:    
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    else:
        print(Gossiping_comments_path + " file exists\n")
        # find the lastRowNum in Gossiping_3500.csv
        lastRowNum = findLastRowNum(Gossiping_comments_path, articleDF)

    for i in trange(lastRowNum, articleLen):
        href = "https://www.ptt.cc{}".format(articleDF.iloc[i]["link"])         # get the link
        aid = str(articleDF.iloc[i]['aid'])                                     # aid is the id of this article
        print(aid + " | link: " + href)
        try:
            resp = fetchData(href)
        except Exception:
            print(Exception)
        
        soup = BeautifulSoup(resp, 'html.parser')
        # metaLine = soup.select('.article-metaline .article-meta-value')
        
        # author = metaLine[0].text
        # artical = metaLine[1].text
        # postTime = metaLine[2].text

        comments = crawlerComment(soup, aid)
        appendListToCSV(Gossiping_comments_path, comments)

    print("The END of the code...")
