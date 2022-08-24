import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class TweetAnalyze:
    def __init__(self):
        self.df = None

    def load_tweets(self):
        self.df = pd.read_csv("tweets.csv")

    def count_analysis(self, type="tweet", start_time=None, end_time=None, step=30, n=5):
        category_title = ["ReplyTweet", "ReTweet", "DirectTweet", "ReTweetWComment"]
        count_list_like_r, count_list_like, count_list_rt, count_list_tweet = [], [], [], []
        date = []
        tweets = []
        dict_interaction = {}
        start, end, end_temp = self.time_arrange(start_time, end_time, step)

        while start < end:
            date.append((start + timedelta(seconds=1)).strftime("%Y-%m-%d"))

            df_temp = self.df[(self.df.date > str(start)) & (self.df.date < str(end_temp))]

            count_list_like_r.append(df_temp.like_count.sum())
            count_list_rt.append(df_temp.rt_count.sum())
            count_list_tweet.append(df_temp.shape[0])
            dict_interaction = self.interaction_dict(df_temp, dict_interaction)
            tweets.append(self.category_dict(df_temp))

            start += timedelta(days=step)
            end_temp += timedelta(days=step)

        df_interaction = pd.DataFrame(data=dict_interaction.values(), index=dict_interaction.keys(), columns=["Count"])
        df_most_interacted = df_interaction.sort_values(by="Count", ascending=False)[:n]

        if type == "like_r":
            self.visualize_count_analysis(title="LikeCount-Date (Received) (" + str(step) + " step)", data_x=date, data_y=count_list_like_r)
        elif type == "like":
            self.visualize_count_analysis(title="LikeCount-Date (" + str(step) + " step)", data_x=date, data_y=count_list_like)
        elif type == "rt_r":
            self.visualize_count_analysis(title="RTCount-Date (Received) (" + str(step) + " step)", data_x=date, data_y=count_list_rt)
        elif type == "tweet":
            self.visualize_count_analysis(title="TweetCount-Date (" + str(step) + " step)", data_x=date, data_y=count_list_tweet)
        elif type == "detailed_tweet":
            self.visualize_count_analysis(title="DetailedTweetCount-Date (" + str(step) + " step)", data_x=date, data_y=self.detailed_tweets_dict(tweets))
        elif type == "interaction":
            self.visualize_count_analysis(title="Interaction (user to others)", data_x=df_most_interacted.index, data_y=df_most_interacted.Count)
            return df_most_interacted.index
        return None

    def date_format(self, str):
        return str[:19]

    def return_by_time(self, df, time):
        indexes = []
        for i in range(df.shape[0]):
            if df.date.iloc[i][:10] == time:
                indexes.append(i)
        return df.iloc[indexes]

    def plot_bar(self, data_x=None, data_y=None, title="Bar plot", fig_size=(10, 6), label_y="ylabel", labelx="xlabel", xticks_rot=45):
        plt.figure(figsize=fig_size)
        plt.title(title)
        plt.bar(data_x, data_y)
        plt.ylabel(label_y)
        plt.xlabel(labelx)
        plt.xticks(rotation=xticks_rot)
        plt.tight_layout()
        plt.show()

    def plot_multi_bar(self, data_x=None, dict_data=None, title="Bar plot", fig_size=(10, 6), label_y="ylabel", labelx="xlabel", xticks_rot=45):
        plotdata = pd.DataFrame(dict_data, index=data_x)
        plotdata.plot(kind="bar", figsize=fig_size)
        plt.title(title)
        plt.ylabel(label_y)
        plt.xlabel(labelx)
        plt.xticks(rotation=xticks_rot)
        plt.tight_layout()
        plt.show()

    def fav_count_dict(self, df, dict_):
        series_fav = df["from"].value_counts()
        for i in range(len(series_fav)):
            if series_fav.index[i] in dict_.keys():
                dict_[series_fav.index[i]] = dict_[series_fav.index[i]] + series_fav[i]
            else:
                dict_[series_fav.index[i]] = series_fav[i]
        return dict_

    def interaction_dict(self, df, dict_):
        series_interaction = df[df.category != "DirectTweet"]["from"].value_counts()
        for i in range(len(series_interaction)):
            if series_interaction.index[i] in dict_.keys():
                dict_[series_interaction.index[i]] = dict_[series_interaction.index[i]] + series_interaction[i]
            else:
                dict_[series_interaction.index[i]] = series_interaction[i]
        return dict_

    def category_dict(self, df):
        available_category_titles = list(df.category.value_counts().index)
        dict_ = {}
        for ct in available_category_titles:
            dict_[ct] = df.category.value_counts()[ct]
        return dict_

    def detailed_tweets_dict(self, list_):
        category_title = ["ReplyTweet", "ReTweet", "DirectTweet", "ReTweetWComment"]
        list_ct_0, list_ct_1, list_ct_2, list_ct_3 = [], [], [], []

        for tw in list_:
            list_ct_0.append(tw[category_title[0]]) if category_title[0] in tw.keys() else list_ct_0.append(0)
            list_ct_1.append(tw[category_title[1]]) if category_title[1] in tw.keys() else list_ct_1.append(0)
            list_ct_2.append(tw[category_title[2]]) if category_title[2] in tw.keys() else list_ct_2.append(0)
            list_ct_3.append(tw[category_title[3]]) if category_title[3] in tw.keys() else list_ct_3.append(0)

        d = {category_title[0]: list_ct_0,
             category_title[1]: list_ct_1,
             category_title[2]: list_ct_2,
             category_title[3]: list_ct_3}
        return d

    def visualize_count_analysis(self, title, data_x, data_y):
        if title[:18] == "DetailedTweetCount":
            self.plot_multi_bar(data_x=data_x, dict_data=data_y, title=title, fig_size=(12, 8), label_y="Tweet count", labelx="Date (Starting)")
        else:
            self.plot_bar(data_x=data_x, data_y=data_y, title=title, label_y='Like count', labelx='Date (Starting)')

    def time_arrange(self, start_time=None, end_time=None, step=30):
        if start_time != None and end_time != None:
            start = datetime.fromisoformat(start_time) - timedelta(seconds=1)
            end = datetime.fromisoformat(end_time)
            end_temp = datetime.fromisoformat(start_time) + timedelta(days=step)
        elif start_time == None and end_time == None:
            start = datetime.fromisoformat(self.df.sort_values(by="date").iloc[0].date[:10]) - timedelta(seconds=1)
            end = datetime.fromisoformat(self.df.sort_values(by="date", ascending=False).iloc[0].date[:10])
            end_temp = datetime.fromisoformat(self.df.sort_values(by="date").iloc[0].date[:10]) + timedelta(days=step)
        return (start, end, end_temp)

    def category_percentage(self):
        total = self.df.shape[0]
        rp_prop = self.df.category.value_counts().ReplyTweet / total
        rt_prop = self.df.category.value_counts().ReTweet / total
        t_prop = self.df.category.value_counts().DirectTweet / total
        rtwc_prop = self.df.category.value_counts().ReTweetWComment / total
        list_by_category = [rp_prop, rt_prop, t_prop, rtwc_prop]
        title = ["ReplyTweet", "ReTweet", "DirectTweet", "ReTweetWComment"]
        plt.figure(figsize=(10, 6))
        plt.title("Percentage by Category")
        plt.bar(title, list_by_category)
        plt.show()


