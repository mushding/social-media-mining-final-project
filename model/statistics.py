from data_process import load_edge_csv, load_node_csv
from matplotlib import pyplot as plt

import pandas as pd

artical_path = '../data/cralwer/Gossiping_20000.csv'
comments_path = '../data/cralwer/Gossiping_20000_comments.csv'

user_mapping = load_node_csv(comments_path, index_col='userid')
artical_mapping = load_node_csv(artical_path, index_col='aid')
num_users, num_articals = len(user_mapping), len(artical_mapping)

edge_index = load_edge_csv(
    comments_path,
    src_index_col='userid',
    src_mapping=user_mapping,
    dst_index_col='aid',
    dst_mapping=artical_mapping,
    link_index_col='tag'
)
print("User number: ", len(user_mapping))
print("Artical number:", len(artical_mapping))
print("Edge number:", edge_index.size())


# What should I do ...
# 對著 src 跑一遍 O(n)
# 對每個 src 做一個 list 來儲存他看過的 dst，如果有新的 dst 才儲存到 list
def statistics(edge_index):
    """ Count the number of article every user read

    Args:
        edge_index (dict): mapping between user id and item id

    Returns:
        user_read_articles (dict):
            key: user_id, value (list): every item this user read
        user_read_count (dict):
            key: user_id, value (list): number of item this user read
    """

    user_read_articles = dict()
    user_read_count = dict()
    for i in range(len(edge_index[0])):
        user_id = edge_index[0][i]
        item_id = edge_index[1][i]
        if (user_id not in user_read_articles.keys()):
            user_read_articles[user_id] = [item_id]
            user_read_count[user_id] = 1
        else:
            if (item_id not in user_read_articles[user_id]):
                user_read_articles[user_id].append(item_id)
                user_read_count[user_id] += 1
    
    return user_read_articles, user_read_count


if __name__ == "__main__":
    edge_index = edge_index.tolist()
    user_read_articles, user_read_count = statistics(edge_index)
    print(len(user_read_articles))
    
    df = pd.DataFrame(user_read_count.items(), columns=['uid', 'article_count'])
    count_df = pd.DataFrame(list(zip(df['article_count'].value_counts().keys(), df['article_count'].value_counts())), columns=['comment_count', 'user_count'])
    count_df = count_df.sort_values(by='comment_count')
    print(count_df)
