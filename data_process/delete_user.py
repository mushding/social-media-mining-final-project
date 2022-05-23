import pandas as pd
import matplotlib.pyplot as plt

def print_info(user_count):
    quartile = user_count.quantile([0.25, 0.5, 0.75])
    print(f"Number of Users: {len(user_count)}")
    print(f"User number of '1' Comments: {(user_count.values == 1).sum()}")
    print(f"User number below '10' Comments: {(user_count.values < 10).sum()}")
    print(f"Quartile Statistic: \n{quartile}")
    plt.plot(user_count.values)
    plt.xlabel("User index")
    plt.ylabel("comments count (num)")
    plt.savefig('image/comments_count.png')


if __name__ == '__main__':

    comments_path = '../data/crawler/Filtered_Gossiping_20000_comments.csv'
    save_path = '../data/crawler/Filtered_Gossiping_comments.csv'
    comments_thred = 20

    df = pd.read_csv(comments_path)

    user_count = df.value_counts('userid')
    df = df.set_index('userid').join(user_count.rename('count'))
    df.drop('Unnamed: 0', inplace=True, axis=1)
    
    df_mask = df['count'] > comments_thred
    filtered_df = df[df_mask]
    filtered_df.to_csv(save_path)
    
    print_info(user_count)
    print(f"Number of Comment: {len(df)}")
    print(f"Number of Filtered Comment: {len(filtered_df)}")
