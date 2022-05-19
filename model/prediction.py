from data_process import load_node_csv, load_edge_csv
import torch
import pandas as pd

from model import LightGCN

from evaluation import get_user_positive_items

def make_predictions(user_id, num_recs, num_pred):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    artical_path = '../data/crawler/Filtered_Gossiping_20000.csv'
    comments_path = '../data/crawler/Filtered_Gossiping_comments.csv'
    # artical_path = '../data/crawler/Gossiping_20000.csv'
    # comments_path = '../data/crawler/Gossiping_20000_comments.csv'
    model_path = '../save/lr_decay=10000'

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
    edge_index = edge_index.to(device)

    model = LightGCN(num_users, num_articals, 64, 3)
    model = model.to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    df = pd.read_csv(artical_path)
    artical_title = pd.Series(df.title.values,index=df.aid).to_dict()

    user_pos_items = get_user_positive_items(edge_index)
    
    user = user_mapping[user_id]
    e_u = model.users_emb.weight[user]
    scores = model.items_emb.weight @ e_u

    print(f"user_pos_items number: {len(user_pos_items[user])}")
    values, indices = torch.topk(scores, k=len(user_pos_items[user]) + num_recs)

    articals = [index.cpu().item() for index in indices if index in user_pos_items[user]][:num_recs]
    artical_ids = [list(artical_mapping.keys())[list(artical_mapping.values()).index(artical)] for artical in articals]
    titles = [artical_title[id] for id in artical_ids]
    print(titles)

    print(f"Here are some articals that user {user_id} rated highly")
    for i in range(num_recs):
        print(f"title: {titles[i]}")

    print()

    articals = [index.cpu().item() for index in indices if index not in user_pos_items[user]][:num_pred]
    artical_ids = [list(artical_mapping.keys())[list(artical_mapping.values()).index(artical)] for artical in articals]
    titles = [artical_title[id] for id in artical_ids]

    print(f"Here are some suggested articals for user {user_id}")
    for i in range(num_pred):
        print(f"title: {titles[i]}")

if __name__ == '__main__':
    USER_ID = 'kirbycopy'
    NUM_RECS = 4
    NUM_PRED = 10
    make_predictions(USER_ID, NUM_RECS, NUM_PRED)