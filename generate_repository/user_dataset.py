import pandas as pd
import csv


def user_dict(data_path):
    data = pd.read_csv(data_path)
    user_dict = {}
    user_id = 0
    for i in range(len(data)):
        user_name = data.iloc[i]["userid"]
        if (not user_dict.get(user_name)):
            user_dict[user_name] = user_id
            user_id += 1
    return user_dict

def saveToCSV(path, dict):
    with open(path, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['userId', 'userName'])
        for key in dict:
            writer.writerow([dict[key], key])

if __name__ == "__main__":
    data_path = "../data/cralwer/Gossiping_100_comments.csv"
    user_dict = user_dict(data_path)

    # save to csv
    csv_path = "../data/repository/user_data.csv"
    saveToCSV(csv_path, user_dict)
