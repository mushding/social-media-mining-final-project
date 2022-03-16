import csv
from crawler_artical import fetchData
import pandas as pd

with open('./Gossiping_100.csv', newline='') as csvfile:

  rows = csv.DictReader(csvfile)

  # 以迴圈輸出指定欄位
  for row in rows:
    href = "https://www.ptt.cc{}".format(row["link"])
    resp = fetchData(href)
    