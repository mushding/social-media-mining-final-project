import pandas as pd

def countComments(article_df):
    article_df = pd.DataFrame(list(zip(article_df['aid'].value_counts().keys(), article_df['aid'].value_counts())), columns=['aid', 'comments_count'])
    article_df = article_df.sort_values(by='aid', ignore_index=True)
    return article_df

def articleFilter(article_df):
    # 把前 25% 的留言數的文章去掉
    threshold = article_df['comments_count'].quantile([0.25]).iloc[0]
    article_df = article_df[article_df['comments_count'] > threshold]
    article_df = article_df.reset_index(drop=True)
    return article_df

def combine(df, article_df):
    df_index = 0
    article_df_index = 0
    new_df = pd.DataFrame()

    for _ in range(len(df)):
        if df['aid'][df_index] == article_df['aid'][article_df_index]:
            df.loc[df_index, 'commentsCount'] = article_df['comments_count'][article_df_index]
            new_df = pd.concat([new_df, df[df_index:df_index+1]], axis=0)
            df_index += 1
            article_df_index += 1
        else:
            df_index += 1
    
    return new_df

def commentsFilter(article_df, comments_df):
    aid = article_df['aid'].tolist()
    new_df = comments_df[comments_df['aid'].isin(aid)]
    return new_df


if __name__ == "__main__":
    file_path = "./data/crawler/Gossiping_20000.csv"
    comments_file_path = "./data/crawler/Gossiping_20000_comments.csv"
    
    df = pd.read_csv(file_path)
    comments_df = pd.read_csv(comments_file_path)
    
    article_df = countComments(comments_df)
    print(article_df['comments_count'].quantile([0.25, 0.5, 0.75]))
    
    article_df = articleFilter(article_df)

    print("Number of article before filtering: ", len(df))
    print("Nubmer of article after filtering: ", len(article_df))
    # df = combine(df, article_df)
    # print(df.shape)

    # article_save_path = "./data/crawler/Filtered_Gossiping_20000.csv"
    # df.to_csv(article_save_path)

    print("Number of comment before filtering", len(comments_df))
    comments_df = commentsFilter(article_df, comments_df)
    print("Number of comment after filtering", len(comments_df))
    
    comments_save_path = "./data/crawler/Filtered_Gossiping_20000_comments.csv"
    comments_df.to_csv(comments_save_path)