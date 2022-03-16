# social-media-mining-final-project

PPT 關鍵字分析

### crawler_artical.py
找文章列表
```
aid       文章 id -> 網址 index + 文章順序
push      討論推/噓熱門度 
title     文章標題
author    文章作者
ip        五章作者發文 ip
postTime  發文時間
link      文章連結
content   文章內容
```

### crawler_content.py
找內文
aid, author, title, postTime, content

找流言
aid, push, uid, comment, ip, time