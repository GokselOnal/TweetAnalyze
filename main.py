import warnings
from pandas.core.common import SettingWithCopyWarning
from sklearn.exceptions import ConvergenceWarning
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action="ignore", category=ConvergenceWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

from GetTweets import *
from TweetAnalyzer import *
from SentimentAnalyzer import *
from TopicModelling import *

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_rows', 200)
pd.set_option('display.float_format', lambda x: '%.2f' % x)


get_tweets = GetTweets()
get_tweets.tweepy_api()

def get_tweets_from(username, startdate, enddate):
    get_tweets.tweepy_api(username)
    get_tweets.user_info(get_tweets.user)
    get_tweets.create_df_tweets(start_date=startdate,
                                end_date=enddate,
                                screen_name=get_tweets.user.screen_name)

def count_analyzer():
    tweet_analyzer = TweetAnalyze()
    tweet_analyzer.load_tweets()

    tweet_analyzer.category_percentage()

    tweet_analyzer.count_analysis(type="like_r",
                                  start_time="2022-05-01",
                                  end_time="2022-08-20",
                                  step=7)

    tweet_analyzer.count_analysis(type="rt_r",
                                  start_time="2022-05-01",
                                  end_time="2022-08-20",
                                  step=7)

    tweet_analyzer.count_analysis(type="detailed_tweet",
                                  start_time="2022-05-01",
                                  end_time="2022-08-20",
                                  step=7)

    tweet_analyzer.count_analysis(type="interaction",
                                  start_time="2022-05-01",
                                  end_time="2022-08-20",
                                  n=10)

def topic_modelling(n_topic):
    topic_model = TopicModelling()
    topic_model.load_tweets()
    topic_model.preprocess()
    topic_model.feature_extraction()
    topic_model.prep()
    topic_model.vectorizer()
    topic_model.model_fit()
    df_topics = topic_model.display_topics(topic_model.model,
                                           topic_model.feature_names_tf,
                                           n_topic)
    print(df_topics)

def sentiment_analyzer(words):
    sentiment_analysis = SentimentAnalysis(get_tweets.api)
    sentiment_analysis.load_tweets()
    df = sentiment_analysis.update_df(sentiment_analysis.get_tweets(words))
    sentiment_analysis.show_words(df)
    sentiment_analysis.show_results(df)

def pipeline():
    get_tweets_from(username="elonmusk", startdate="2022-05-01", enddate="2022-08-20")
    count_analyzer()
    topic_modelling(n_topic=10)
    sentiment_analyzer(words="Tesla")

if __name__ == '__main__':
    pipeline()

