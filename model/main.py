from data_process import load_edge_csv, load_node_csv, split_dataset, COO2SparseTensor
from model import LightGCN
from train import train
from test import test
from prediction import make_predictions

import wandb
import argparse
from pathlib import Path

import torch
from torch import optim

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="wandb run name", required=True)
parser.add_argument("--iteration", help="traning iteration", type=int, required=True)
parser.add_argument("--batch-size", help="set batch size", type=int, required=True)
parser.add_argument("--lr-decay", help="learning rate decay", type=int, required=True)
parser.add_argument("--K", help="graph's neighbor k", type=int, required=True)
parser.add_argument("--embedding", help="user item embedding", type=int, required=True)
parser.add_argument("--lambdas", help="L2 regularization lambda", type=float, required=True)
args = parser.parse_args()

# <PTT Gossiping>
# artical_path = '../data/cralwer/Gossiping_20000.csv'
# comments_path = '../data/cralwer/Gossiping_200_comments.csv'
artical_path = '../data/crawler/Filtered_Gossiping_20000.csv'
comments_path = '../data/crawler/Filtered_Duplicate_Gossiping_comments.csv'

user_mapping = load_node_csv(comments_path, index_col='userid')
artical_mapping = load_node_csv(artical_path, index_col='aid')
num_users, num_articals = len(user_mapping), len(artical_mapping)

edge_info = load_edge_csv(
    comments_path,
    src_index_col='userid',
    src_mapping=user_mapping,
    dst_index_col='aid',
    dst_mapping=artical_mapping,
    link_index_cols=['tag', 'commentNum']
)

# <MovieLens>
# movie_path = '../data/movielens_1M/movies.csv'
# rating_path = '../data/movielens_1M/ratings.csv'

# user_mapping = load_node_csv(rating_path, index_col='userId')
# artical_mapping = load_node_csv(movie_path, index_col='movieId')
# num_users, num_articals = len(user_mapping), len(artical_mapping)

# edge_index = load_edge_csv(
#     rating_path,
#     src_index_col='userId',
#     src_mapping=user_mapping,
#     dst_index_col='movieId',
#     dst_mapping=artical_mapping,
#     link_index_col='rating'
# )

print("User number: ", len(user_mapping))
print("Artical number:", len(artical_mapping))
print("Edge number:", edge_info[0].size())

train_edge_info, val_edge_info, test_edge_info = split_dataset(edge_info)
train_sparse_edge_index, val_sparse_edge_index, test_sparse_edge_index = COO2SparseTensor(
    train_edge_info, val_edge_info, test_edge_info, num_users, num_articals)

edge_index, _ = edge_info
train_edge_index, _ = train_edge_info
val_edge_index, _ = val_edge_info
test_edge_index, _ = test_edge_info

# define contants
contants = {
    "ITERATIONS": args.iteration,
    "BATCH_SIZE": args.batch_size,
    "LR": 0.005,
    "ITERS_PER_EVAL": 200,
    "ITERS_PER_LR_DECAY": args.lr_decay,
    "K": args.K,
    "EMBEDDING_DIM": args.embedding,
    "LAMBDA": args.lambdas,
}

model = LightGCN(num_users, num_articals, embedding_dim=contants["EMBEDDING_DIM"], K=contants["K"])

wandb.init(
    project="LightGCN", 
    entity="mushding",
    name=args.name,
    config=contants
)

# setup
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device {device}.")


model = model.to(device)
model.train()

optimizer = optim.Adam(model.parameters(), lr=contants['LR'])
scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)

edge_index = edge_index.to(device)
train_edge_index = train_edge_index.to(device)
train_sparse_edge_index = train_sparse_edge_index.to(device)

val_edge_index = val_edge_index.to(device)
val_sparse_edge_index = val_sparse_edge_index.to(device)

train(model, optimizer, scheduler, train_sparse_edge_index, train_edge_index, val_sparse_edge_index, val_edge_index, contants, device)

save_path = Path('../save') / args.name
torch.save(model.state_dict(), save_path)

test(model, device, train_edge_index, val_edge_index, test_edge_index, test_sparse_edge_index, contants)