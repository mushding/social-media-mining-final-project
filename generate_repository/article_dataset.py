import pandas as pd
import csv

path = "../data/cralwer/Gossiping_100.csv"
df = pd.read_csv(path, index_col='aid')
mapping = {index: i for i, index in enumerate(df.index.unique())}

def saveToCSV(path, dict):
    with open(path, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['articalId', 'webId'])
        for key in dict:
            writer.writerow([dict[key], key])

# save to csv
csv_path = "../data/repository/artical_data.csv"
saveToCSV(csv_path, mapping)