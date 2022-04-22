from cmath import exp
import csv
import imp
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
        # "推" is hl push-tag, "噓" is 'f1 hl push-tag'
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

# 找現有 csv 的最後一行
def findLastRow(article_rows):
    with open('./Gossiping_3500_comments.csv', newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        listrows = list(rows)
        last_row_aid = listrows[-1]['aid']
        same_aid = list()
        for i in range(len(article_rows)):
            if article_rows[i]['aid'] == last_row_aid:
                same_aid.append(i)
        return same_aid[-1] + 2

# 儲存新的 comment 到 csv。若沒有csv檔會創一個新的，已有csv檔會新增新的comment到裡面
def addDictToCSV(path, commentsList):
    file = Path(path)
    if (file.exists()):
        lastRowNum = findLastRow()
        appendDictToCSV(commentsList)

# 單純創一個 csv 的空白檔案
def createCSV():
    fieldnames = ['aid', 'tag', 'userid', 'message', 'ip', 'time']
    with open('Gossiping_3500_comments.csv', 'w', encoding='UTF8', newline='') as f:    
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

# 新增新的 comment 到現有的 csv
def appendDictToCSV(commentsList):
    fieldnames = ['aid', 'tag', 'userid', 'message', 'ip', 'time']
    with open('Gossiping_3500_comments.csv', 'a+', newline='') as f:
        dictWriter = csv.DictWriter(f, fieldnames=fieldnames)
        dictWriter.writerows(commentsList)

if __name__ == "__main__":
    Gossiping3500_path = "./data/cralwer/Gossiping_3500.csv"
    Gossiping3500Comment_path = "./data/cralwer/Gossiping_3500_comments.csv"

    with open(Gossiping3500_path, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        listrows = list(rows)
        totalrows = len(listrows)
        last_row = findLastRow(listrows)
        commentsList = list()
        # createCSV()

        # 以迴圈輸出指定欄位
        for i in trange(last_row, totalrows):
            href = "https://www.ptt.cc{}".format(listrows[i]["link"])       # get the link
            print(href)
            aid = listrows[i]['aid']                                        # aid is the id of this article
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
            appendDicttoCSV(comments)

    print("end of the code")
