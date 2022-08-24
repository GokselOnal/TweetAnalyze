import tweepy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import nltk
from nltk import FreqDist
from textblob import TextBlob
import preprocessor as p
from wordcloud import WordCloud, STOPWORDS , ImageColorGenerator

class SentimentAnalysis:
    def __init__(self, api):
        self.df = None
        self.api = api

    def load_tweets(self):
        self.df = pd.read_csv("tweets.csv")

    def preprocess_tweets(self, tweet, stemming=False, lemmatizer=False):
        stopwords = nltk.corpus.stopwords.words('english')
        ps = nltk.PorterStemmer()
        wn = nltk.WordNetLemmatizer()

        temp = tweet.lower()
        temp = p.clean(temp)
        temp = re.sub(r'https\S+', '', temp)
        temp = re.sub(r"rt[\s]", "", temp)
        temp = re.sub('[()!?]', ' ', temp)
        temp = re.sub('\[.*?\]', ' ', temp)
        temp = re.sub("[^a-z0-9]", " ", temp)
        temp = temp.split()
        temp = [word for word in temp if word not in stopwords]
        if stemming:
            temp = [ps.stem(word) for word in temp]
        if lemmatizer:
            temp = [wn.lemmatize(word) for word in temp]
        temp = " ".join(word for word in temp)
        return temp

    def get_tweets(self, content, n=500):
        all_tweets = []
        for tweet in tweepy.Cursor(self.api.search_tweets, q=content, tweet_mode="extended", lang="en").items(n):
            all_tweets.append(tweet.full_text)
        df = pd.DataFrame(all_tweets, columns=["Tweet"])
        df = pd.DataFrame((set(df.Tweet)), columns=["Tweet"])
        return df

    def getSubjectivity(self, text):
        return TextBlob(text).sentiment.subjectivity

    def getPolarity(self, text):
        return TextBlob(text).sentiment.polarity

    def getAnalysis(self, score):
        if score < 0:
            return "Negative"
        elif score == 0:
            return "Neutral"
        else:
            return "Positive"

    def update_df(self, tweets):
        tweets["Clean_Tweet"] = tweets["Tweet"].apply(self.preprocess_tweets)
        tweets["Subjectivity"] = tweets["Clean_Tweet"].apply(self.getSubjectivity)
        tweets["Polarity"] = tweets["Clean_Tweet"].apply(self.getPolarity)
        tweets["Analysis"] = tweets["Polarity"].apply(self.getAnalysis)
        return tweets

    def show_words(self, tweets):
        allWords = " ".join([twts for twts in tweets["Clean_Tweet"]])
        wordCloud = WordCloud(width=500, height=300, random_state=42, max_font_size=119).generate(allWords)

        plt.imshow(wordCloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()

    def show_results(self, tweets):
        tweets["Analysis"].value_counts()

        plt.title("Sentiment Analysis")
        plt.xlabel("Sentiments")
        plt.ylabel("Counts")
        tweets["Analysis"].value_counts().plot(kind="bar")
        plt.show()