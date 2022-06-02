from data_process import load_node_csv, load_edge_csv
import torch
import pandas as pd
from pathlib import Path

from model import LightGCN

from evaluation import get_user_positive_items

def make_predictions(user_indice, num_recs, num_pred):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    text_save_dir = '../result'
    artical_path = '../data/crawler/Filtered_Gossiping_20000.csv'
    comments_path = '../data/crawler/Filtered_Duplicate_Gossiping_comments.csv'
    # artical_path = '../data/crawler/Gossiping_20000.csv'
    # comments_path = '../data/crawler/Gossiping_20000_comments.csv'
    model_path = '../save/item -> 20, user -> 40, (no duplicate) iteration 2000'

    print("------------- 1. Load Node Edge... -------------")
    user_mapping = load_node_csv(comments_path, index_col='userid')
    artical_mapping = load_node_csv(artical_path, index_col='aid')
    # create {index: userid} dict (0: mushding)
    user_mapping_inv = {v: k for k, v in user_mapping.items()}
    
    num_users, num_articals = len(user_mapping), len(artical_mapping)

    edge_info = load_edge_csv(
        comments_path,
        src_index_col='userid',
        src_mapping=user_mapping,
        dst_index_col='aid',
        dst_mapping=artical_mapping,
        link_index_cols=['tag', 'commentNum']
    )
    edge_index, _ = edge_info
    edge_index = edge_index.to(device)

    print("------------- 2. Load Model... -------------")
    model = LightGCN(num_users, num_articals, 512, 3)
    model = model.to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    print("------------- 3. Load Artical Title... -------------")
    df = pd.read_csv(artical_path)
    artical_title = pd.Series(df.title.values,index=df.aid).to_dict()

    print("------------- 4. Get Positive Items... -------------")
    user_pos_items = get_user_positive_items(edge_index)

    print("------------- start user id loop -------------")
    for user_idx in range(user_indice):
        print("------------- 5. Load Target User id/idx... -------------")
        user_id = user_mapping_inv[user_idx]
        print(f"user idx: {user_idx}")
        print(f"user id: {user_id}")
        
        user = user_mapping[user_id]
        e_u = model.users_emb.weight[user]
        scores = model.items_emb.weight @ e_u
        print(f"Len of scores: {len(scores)}")
        print(f"Len of user_pos_items number: {len(user_pos_items[user])}")
        values, indices = torch.topk(scores, k=len(user_pos_items[user]) + num_recs)

        print("------------- 6. Calculating Recommandation... -------------")
        articals = [index.cpu().item() for index in indices if index in user_pos_items[user]][:num_recs]
        artical_ids = [list(artical_mapping.keys())[list(artical_mapping.values()).index(artical)] for artical in articals]
        titles = [artical_title[id] for id in artical_ids]
        
        text_name_path = Path(text_save_dir) / f"{user_idx}_{user_id}.txt"
        
        # write into text file (known edge)
        with open(text_name_path, 'w') as f:
            f.writelines(f"Here are some articals that user {user_id} rated highly\n")
            artical_lens = len(articals) if len(articals) <= 20 else 20
            for i in range(artical_lens):
                f.writelines(f"title: {titles[i]}\n")
            f.writelines("\n")

        # print(f"Here are some articals that user {user_id} rated highly")
        # for i in range(len(articals)):
        #     print(f"title: {titles[i]}")

        # print()

        articals = [index.cpu().item() for index in indices if index not in user_pos_items[user]][:num_pred]
        artical_ids = [list(artical_mapping.keys())[list(artical_mapping.values()).index(artical)] for artical in articals]
        titles = [artical_title[id] for id in artical_ids]

        # write into text file (recommendation edge)
        with open(text_name_path, 'a') as f:
            f.writelines(f"Here are some suggested articals for user {user_id}\n")
            for i in range(num_pred):
                f.writelines(f"title: {titles[i]}\n")

        # print(f"Here are some suggested articals for user {user_id}")
        # for i in range(num_pred):
        #     print(f"title: {titles[i]}")

if __name__ == '__main__':
    USER_IDX = 200
    NUM_RECS = 200
    NUM_PRED = 100

    make_predictions(USER_IDX, NUM_RECS, NUM_PRED)