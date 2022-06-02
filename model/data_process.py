import pandas as pd

import torch
from torch_sparse import SparseTensor

from sklearn.model_selection import train_test_split


# load user and movie nodes
def load_node_csv(path, index_col):
    """Loads csv containing node information

    Args:
        path (str): path to csv file
        index_col (str): column name of index column

    Returns:
        dict: mapping of csv row to node id
    """
    df = pd.read_csv(path, index_col=index_col)
    mapping = {index: i for i, index in enumerate(df.index.unique())}
    return mapping


# load edges between users and movies
def load_edge_csv(path, src_index_col, src_mapping, dst_index_col, dst_mapping, link_index_cols):
    """Loads csv containing edges between users and items

    Args:
        path (str): path to csv file
        src_index_col (str): column name of users
        src_mapping (dict): mapping between row number and user id
        dst_index_col (str): column name of items
        dst_mapping (dict): mapping between row number and item id
        link_index_col (str): column name of user item interaction
        rating_threshold (int, optional): Threshold to determine positivity of edge. Defaults to 4.

    Returns:
        torch.Tensor: 2 by N matrix containing the node ids of N user-item edges
    """
    df = pd.read_csv(path)
    edge_index = None
    src = [src_mapping[index] for index in df[src_index_col]]
    dst = [dst_mapping[index] for index in df[dst_index_col]]

    tag_mapping = {
        '噓': 1,
        '→': 2,
        '推': 4
    }
    tag_header = link_index_cols[0]
    commentNum_header = link_index_cols[1]

    tag = [tag_mapping[tag] for tag in df[tag_header]]
    commentNum = [i for i in df[commentNum_header]]
    edge_attr = [t * cn for (t, cn) in zip(tag, commentNum)]
    edge_attr = torch.tensor(edge_attr).to(torch.float32)
    edge_index = [[], []]
    for i in range(edge_attr.shape[0]):
        if edge_attr[i]:
            edge_index[0].append(src[i])
            edge_index[1].append(dst[i])

    return torch.tensor(edge_index), edge_attr


def split_dataset(edge_info):
    """split dataset to Traning Testing Validation set

    Args:
        edge_info (dict, dict): 
            edge_index, edge_attr
            edge_index: 2 by N 
            edge_attr:  N by 1
    Returns:
        torch.Tensor: 2 by N matrix for Training 80
        torch.Tensor: 2 by N matrix for Testing 10
        torch.Tensor: 2 by N matrix for Validation 10
    """
    edge_index, edge_attr = edge_info
    num_interactions = edge_index.shape[1]
    all_indices = [i for i in range(num_interactions)]

    train_indices, test_indices = train_test_split(
        all_indices, test_size=0.2, random_state=1)
    val_indices, test_indices = train_test_split(
        test_indices, test_size=0.5, random_state=1)

    train_edge_index = edge_index[:, train_indices]
    val_edge_index = edge_index[:, val_indices]
    test_edge_index = edge_index[:, test_indices]

    train_edge_attr = edge_attr[train_indices]
    val_edge_attr = edge_attr[val_indices]
    test_edge_attr = edge_attr[test_indices]

    print(f"Train: \nIndex: {train_edge_index.shape} \nAttr: {train_edge_attr.shape}")
    print(f"Val: \nIndex: {val_edge_index.shape} \nAttr: {val_edge_attr.shape}")
    print(f"Test: \nIndex: {test_edge_index.shape} \nAttr: {test_edge_attr.shape}")

    return (train_edge_index, train_edge_attr), \
           (val_edge_index, val_edge_attr),\
           (test_edge_index, test_edge_attr)


def COO2SparseTensor(train_edge_info, test_edge_info, val_edge_info, num_users, num_articals):
    """convert COO format (2, N) to (u + i, u + i) Square Matrix

    Args:
        train_edge_index (torch.Tensor): 2 by N matrix for Training 80
        test_edge_index (torch.Tensor): 2 by N matrix for Testing 10
        val_edge_index (torch.Tensor): 2 by N matrix for Validation 10
        user_mapping (dict): userid to id mapping
        artical_mapping (dict): aid to id mapping

    Returns:
        torch.Tensor: (u + i, u + i) matrix for Training 80
        torch.Tensor: (u + i, u + i) matrix for Testing 10
        torch.Tensor: (u + i, u + i) matrix for Validation 10
    """
    train_edge_index, train_edge_attr = train_edge_info
    val_edge_index, val_edge_attr = test_edge_info
    test_edge_index, test_edge_attr = val_edge_info

    # convert edge indices into Sparse Tensors: https://pytorch-geometric.readthedocs.io/en/latest/notes/sparse_tensor.html
    train_sparse_edge_index = SparseTensor(row=train_edge_index[0], col=train_edge_index[1], value=train_edge_attr, sparse_sizes=(
        num_users + num_articals, num_users + num_articals))
    val_sparse_edge_index = SparseTensor(row=val_edge_index[0], col=val_edge_index[1], value=val_edge_attr, sparse_sizes=(
        num_users + num_articals, num_users + num_articals))
    test_sparse_edge_index = SparseTensor(row=test_edge_index[0], col=test_edge_index[1], value=test_edge_attr, sparse_sizes=(
        num_users + num_articals, num_users + num_articals))

    # train_sparse_edge_index = SparseTensor(row=train_edge_index[0], col=train_edge_index[1], sparse_sizes=(
    #     num_users + num_articals, num_users + num_articals))
    # val_sparse_edge_index = SparseTensor(row=val_edge_index[0], col=val_edge_index[1], sparse_sizes=(
    #     num_users + num_articals, num_users + num_articals))
    # test_sparse_edge_index = SparseTensor(row=test_edge_index[0], col=test_edge_index[1], sparse_sizes=(
    #     num_users + num_articals, num_users + num_articals))

    return train_sparse_edge_index, val_sparse_edge_index, test_sparse_edge_index
