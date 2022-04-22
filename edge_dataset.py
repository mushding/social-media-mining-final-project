import pandas as pd
import numpy as np
import torch
# from sentence_transformers import SentenceTransformer

user_path = "./data/repository/user_data.csv"
user_df = pd.read_csv(user_path, index_col='userName', squeeze=True)
user_dict = user_df.to_dict()

artical_path = "./data/repository/artical_data.csv"
artical_df = pd.read_csv(artical_path, index_col='webId', squeeze=True)
artical_dict = artical_df.to_dict()

comments_path = "./data/cralwer/Gossiping_100_comments.csv"
comments_df = pd.read_csv(comments_path, index_col=None, squeeze=True)

# edge_index
userList = [user_dict[comment] for comment in comments_df.userid]
articalList = [artical_dict[comment]for comment in comments_df.aid]
edge_index = torch.tensor([userList, articalList])

# edge_attr
# message = comments_df.message.to_list()
# model = SentenceTransformer('distiluse-base-multilingual-cased-v2', device='cuda')
# # TODO: Add new attr
# message_attr = model.encode(message, show_progress_bar=True, convert_to_tensor=True, device='cuda')
