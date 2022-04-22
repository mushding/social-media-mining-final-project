import pandas as pd
from sentence_transformers import SentenceTransformer

from torch_geometric.data import HeterData
import torch

class SequenceEncoder:
    def __init__(self, model_name='distiluse-base-multilingual-cased-v2', device=None):
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)

    @torch.no_grad()
    def __call__(self, df):
        x = self.model.encode(df.values, show_progress_bar=True, convert_to_tensor=True, device=self.device)
        return x.cpu()

def load_node_csv(path, index_col, encoders=None, **kwargs):
    df = pd.read_csv(path, index_col=index_col)

    mapping = {index: i for i, index in enumerate(df.index.unique())}

    x = None
    if encoders is not None:
        xs = [encoder(df[col]) for col, encoder in encoders.items()]
        x = torch.cat(xs, dim=-1)
    return x, mapping

def load_edge_csv(path, src, dst, encoders=None):
    comments_df = pd.read_csv(path, squeeze=True)

    userList = [user_dict[comment] for comment in comments_df.userid]
    articalList = [artical_dict[comment]for comment in comments_df.aid]
    edge_index = torch.tensor([userList, articalList])

    x = None
    if encoders is not None:
        xs = [encoder(df[col]) for col, encoder in encoders.items()]
        x = torch.cat(xs, dim=-1)
    return edge_index, edge_attr

if __name__ == "__main__":
    # user.num_node
    user_path = "./data/repository/user_data.csv"
    user_x, user_mapping = load_node_csv(user_path, index_col='userId')

    # artical.x
    artical_path = "./data/cralwer/Gossiping_100.csv"
    artical_x, artical_mapping = load_node_csv(
        artical_path, 
        index_col='aid',
        encoders={
            'title':  SequenceEncoder(),
            'content': SequenceEncoder(),
        })

    # (user, comments, artical).edge_index
    # (user, comments, artical).edge_attr
    user_path = "./data/repository/user_data.csv"
    user_df = pd.read_csv(user_path, index_col='userName', squeeze=True)
    user_dict = user_df.to_dict()
    artical_path = "./data/repository/artical_data.csv"
    artical_df = pd.read_csv(artical_path, index_col='webId', squeeze=True)
    artical_dict = artical_df.to_dict()
    
    comments_path = "./data/cralwer/Gossiping_100_comments.csv"
    edge_index, edge_attr = load_edge_csv(comments_path, user_dict, artical_dict, encoders={
        'message': SequenceEncoder()
    })

    # Set Pytorch Geometric Data Set
    data = HeterData()

    data['user'].num_nodes = len(user_mapping)
    data['artical'].x = artical_x
    data['user', 'comments', 'artical'].edge_index = edge_index
    data['user', 'comments', 'artical'].edge_attr = edge_attr

    print(data)
