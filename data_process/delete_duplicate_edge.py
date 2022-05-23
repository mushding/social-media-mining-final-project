import pandas as pd
import csv

def delete_duplicate_edge(df):
    prev_index = 0
    data = {'userid': [], 'aid': [], 'tag': [], 'commentNum': []}
    sum = 1

    for index in range(len(df)):
        aid = df['aid'][index]
        prev_aid = df['aid'][prev_index]
        if (aid != prev_aid):
            data['userid'].append(df['userid'][prev_index])
            data['aid'].append(df['aid'][prev_index])
            data['tag'].append(df['tag'][prev_index])
            data['commentNum'].append(sum)
            
            prev_index = index
            sum = 1
        else:
            sum += 1
        print(index)
    
    return data


if __name__ == "__main__":
    file_path = "../data/crawler/Filtered_Gossiping_comments.csv"
    df = pd.read_csv(file_path)

    data = delete_duplicate_edge(df)

    save_file_path = "../data/crawler/Filtered_Duplicate_Gossiping_comments.csv"
    fieldnames = ['userid', 'aid', 'tag', 'commentNum']
    df = pd.DataFrame.from_dict(data)
    df.to_csv (save_file_path, index = False, header=True)
