from pathlib import Path
import pandas as pd

# load user and movie nodes
def load_node_csv(path, index_col, sep=',', header=0):
    """Loads csv containing node information

    Args:
        path (str): path to csv file
        index_col (str): column name of index column

    Returns:
        dict: mapping of csv row to node id
    """
    df = pd.read_csv(path, index_col=index_col, sep=sep, header=header)
    mapping = {index: i for i, index in enumerate(df.index.unique())}
    return mapping

moviesadjkfl_path = Path('./data') / '/movielens_1M/movies.dat'
