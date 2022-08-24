import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer


class TopicModelling:
    def __init__(self):
        self.df = None
        self.tweets_df = None
        self.tf = None
        self.model = None
        self.feature_names_tf = None

    def load_tweets(self):
        self.df = pd.read_csv("tweets.csv")

    def preprocess(self):
        tweets = self.df.text
        tweets_df = pd.DataFrame(tweets)
        tweets_df.shape, tweets_df.text.unique().shape
        tweets_df['is_retweet'] = tweets_df["text"].apply(lambda x: x[:2] == 'RT')
        tweets_df['is_retweet'].sum()
        tweets_df.loc[tweets_df['is_retweet']].text.unique().size
        self.tweets_df = tweets_df.groupby(['text']).size().reset_index(name='counts').sort_values('counts', ascending=False).head(10)

    def find_retweeted(self, tweet):
        return re.findall('(?<=RT\s)(@[A-Za-z]+[A-Za-z0-9-_]+)', tweet)

    def find_mentioned(self, tweet):
        return re.findall('(?<!RT\s)(@[A-Za-z]+[A-Za-z0-9-_]+)', tweet)

    def find_hashtags(self, tweet):
        return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', tweet)

    def feature_extraction(self):
        self.tweets_df['retweeted'] = self.tweets_df.text.apply(self.find_retweeted)
        self.tweets_df['mentioned'] = self.tweets_df.text.apply(self.find_mentioned)
        self.tweets_df['hashtags'] = self.tweets_df.text.apply(self.find_hashtags)

    def remove_links(self, tweet):
        tweet = re.sub(r'http\S+', '', tweet)
        tweet = re.sub(r'bit.ly/\S+', '', tweet)
        tweet = tweet.strip('[link]')
        return tweet

    def remove_users(self, tweet):
        tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet)
        tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet)
        return tweet

    def clean_tweet(self, tweet, bigrams=False):
        my_stopwords = nltk.corpus.stopwords.words('english')
        word_rooter = nltk.stem.snowball.PorterStemmer(ignore_stopwords=False).stem
        my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@'
        tweet = self.remove_users(tweet)
        tweet = self.remove_links(tweet)
        tweet = tweet.lower()
        tweet = re.sub('[' + my_punctuation + ']+', ' ', tweet)
        tweet = re.sub('\s+', ' ', tweet)
        tweet = re.sub('([0-9]+)', '', tweet)
        tweet = re.sub("[^a-z0-9]", " ", tweet)
        tweet_token_list = [word for word in tweet.split(' ') if word not in my_stopwords]

        tweet_token_list = [word_rooter(word) if '#' not in word else word for word in tweet_token_list]
        if bigrams:
            tweet_token_list = tweet_token_list + [tweet_token_list[i] + '_' + tweet_token_list[i + 1] for i in range(len(tweet_token_list) - 1)]
        tweet = ' '.join(tweet_token_list)

        return tweet

    def prep(self):
        self.tweets_df['clean_tweet'] = self.tweets_df.text.apply(self.clean_tweet)

    def vectorizer(self):
        vectorizer = CountVectorizer(token_pattern='\w+|\$[\d\.]+|\S+')
        self.tf = vectorizer.fit_transform(self.tweets_df['clean_tweet']).toarray()
        tf_feature_names = vectorizer.get_feature_names()
        self.feature_names_tf = tf_feature_names

    def model_fit(self):
        model = NMF(n_components=10, random_state=0, alpha=.1, l1_ratio=.5)
        model.fit(self.tf)
        self.model = model

    def display_topics(self, model, feature_names, no_top_words):
        topic_dict = {}
        for topic_idx, topic in enumerate(model.components_):
            topic_dict["Topic %d words" % (topic_idx)] = ['{}'.format(feature_names[i]) for i in topic.argsort()[:-no_top_words - 1:-1]]
            topic_dict["Topic %d weights" % (topic_idx)] = ['{:.1f}'.format(topic[i]) for i in topic.argsort()[:-no_top_words - 1:-1]]
        return pd.DataFrame(topic_dict)
