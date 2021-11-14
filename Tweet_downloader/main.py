import time

from twitter_client import TwitterClient
from tweet_analyzer import TweetAnalyzer
from popular_twitter_accounts import twitter_accounts

def get_twitter_feed(x, y):

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    tweets = twitter_client.get_user_timeline_tweets(x,y)

    tweet_analyzer.set_account(x)

    tweet_analyzer.set_num_of_tweets(y)

    df1 = tweet_analyzer.tweets_to_data_frame1(tweets)

    df2 = tweet_analyzer.tweets_to_data_frame2(tweets)

    # upload the file to firebase
    tweet_analyzer.upload_fire_base(df1, df2)


def main():

    # loop though the desired twitter accounts and download tweets
    for key, value in twitter_accounts.items():
        print("Downloading tweets from @" + value + "...")
        get_twitter_feed(value, 1500)
        print("@" + value + " tweets download completed")
        time.sleep(5) 
    
main()