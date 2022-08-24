import tweepy
import pandas as pd
import datetime
import warnings
import math

class GetTweets:
    def __init__(self):
        self.api = None
        self.user = None

    def tweepy_api(self, target_user_name="#"):
        tweepylog = pd.read_csv("TweepyLog.csv")

        consumer_key = tweepylog["api_key"][0]
        consumer_secret = tweepylog["api_key"][1]
        access_token = tweepylog["access_token"][0]
        access_token_secret = tweepylog["access_token"][1]

        authenticate = tweepy.OAuthHandler(consumer_key, consumer_secret)
        authenticate.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(authenticate, wait_on_rate_limit=True)
        if target_user_name != "#":
            self.user = self.api.get_user(screen_name=target_user_name)

    def user_info(self, user):
        print(f"{user.screen_name}")
        print(f"Username        : {user.name}")
        print(f"Verified account: {user.verified}")
        print(f"Following       : {user.friends_count}")
        print(f"Followers       : {user.followers_count}")
        print(f"Favourites      : {user.favourites_count}")
        print(f"Location        : {user.location}")

    def create_df_tweets(self, start_date, end_date, screen_name):
        from datetime import datetime
        warnings.filterwarnings('ignore')
        df = pd.DataFrame(columns=["id", "text", "date", "like_count", "rt_count", "category", "from"])

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        tweets = []
        tmp_tweets = self.api.user_timeline(screen_name=screen_name, include_rts=True, tweet_mode='extended')
        for tweet in tmp_tweets:
            if tweet.created_at.replace(tzinfo=None) < end and tweet.created_at.replace(tzinfo=None) > start:
                tweets.append(tweet)

        while (tmp_tweets[-1].created_at.replace(tzinfo=None) > start):
            tmp_tweets = self.api.user_timeline(screen_name=self.user.screen_name, max_id=tmp_tweets[-1].id, include_rts=True, tweet_mode='extended')
            for tweet in tmp_tweets:
                if tweet.created_at.replace(tzinfo=None) < end and tweet.created_at.replace(tzinfo=None) > start:
                    tweets.append(tweet)

        for t_object in tweets:
            if t_object.full_text[0:2] == "RT":
                category = "ReTweet"
            elif t_object.in_reply_to_status_id != None and t_object.in_reply_to_screen_name != self.user.screen_name:
                category = "ReplyTweet"
            elif t_object.is_quote_status != False and t_object.in_reply_to_screen_name != self.user.screen_name:
                category = "ReTweetWComment"
            else:
                category = "DirectTweet"

            if hasattr(t_object, "retweeted_status"):
                from_ = t_object.retweeted_status.author.screen_name
            if hasattr(t_object, "quoted_status"):
                from_ = t_object.quoted_status.author.screen_name
            if t_object.in_reply_to_screen_name != None:
                from_ = t_object.in_reply_to_screen_name

            d = {"id": t_object.id,
                 "date": t_object.created_at,
                 "text": t_object.full_text,
                 "like_count": t_object.favorite_count,
                 "like_count": t_object.favorite_count,
                 "rt_count": t_object.retweet_count,
                 "from": from_,
                 "category": category
                 }

            df = df.append(d, ignore_index=True)
            df.to_csv("tweets.csv", index=False)
        return df

    def get_friends(self, screen_name):
        user_ = self.api.get_user(screen_name=screen_name)
        friends = []
        page = math.ceil(user_.friends_count / 200)
        for page in tweepy.Cursor(self.api.get_friends, screen_name=screen_name, count=200).pages(page):
            for user in page:
                friends.append(user.screen_name)
        return set(friends)

    def get_common_friends(self, screen_name1, screen_name2):
        f_user1 = self.get_friends(screen_name1)
        f_user2 = self.get_friends(screen_name2)
        return (f_user1 & f_user2)

    def extract_timeline_as_df(self,timeline_list):
        columns = set()
        allowed_types = [str, int]
        tweets_data = []
        for status in timeline_list:
            status_dict = dict(vars(status))
            keys = vars(status).keys()
            single_tweet_data = {"user": status.user.screen_name}
            for k in keys:
                try:
                    v_type = type(status_dict[k])
                except:
                    v_type = None
                if v_type != None:
                    if v_type in allowed_types:
                        single_tweet_data[k] = status_dict[k]
                        columns.add(k)
            tweets_data.append(single_tweet_data)
        header_cols = list(columns)
        header_cols.append("user")
        df = pd.DataFrame(tweets_data, columns=header_cols)
        return df


