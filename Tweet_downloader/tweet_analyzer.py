"""
Provides functionalities for analyzing and categorizing content from tweets.
"""
from io import StringIO
from io import BytesIO
from textblob import TextBlob

import numpy as np
import pandas as pd               # to be able to store data in data frame
import re                         # regular expression
import datetime
import os
import pyrebase

from company_list import companies, companies_stock_market
from firebase_credentials import config

class TweetAnalyzer():

    '''
    default constructor
    '''
    def __init__(self):
        self._date = str(datetime.date.today())
        self._directory = "default"
        self._tweet_account = ""
        self._num_of_tweets = 0

    # getter method
    def get_account(self):
        return self._tweet_account
    
    def get_num_of_tweets(self):
        return self._num_of_tweets

    def get_directory(self):
        return self._directory

    # setter method
    def set_account(self, x):
        self._tweet_account = x

    def set_num_of_tweets(self, x):
        self._num_of_tweets = x

    # get twitter user name
    def get_user_name(self, val):
        for key, value in popular_twitter_accounts.accounts.items():
            if val == value:
                return key
        return "key doesn't exist"

    # return the file name with its tweet account and number of tweets 
    def get_filename(self):
        return self._date + "_@" + self._tweet_account + "_" + str(self._num_of_tweets) + "_tweets"

    """
    Use regular expression library to clear the text
    - removing special characters from tweets
    - remove hyper links
    """
    def clean_tweet(self, tweet):
        cleaned_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        return cleaned_text

    '''
    save the tweets to data frame of: tweet, id, len, date, source, likes, retweets
    '''
    def tweets_to_data_frame1(self, tweets):

        # extract the texts from each of those tweets
        df = pd.DataFrame(data=[self.clean_tweet(tweet.full_text) for tweet in tweets], columns=['tweets'])

        # id
        df['id'] = np.array([tweet.id for tweet in tweets]) 
        
        # length
        df['len'] = np.array([len(tweet.full_text) for tweet in tweets])
       
        # date
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        
        # source
        df['source'] = np.array([tweet.source for tweet in tweets])
        
        # number of likes
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        
        # number of retweet
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df

    '''
    save the tweets to data frame of: tweet, date, source, likes, retweets
    '''
    def tweets_to_data_frame2(self, tweets):

        # extract the texts from each of those tweets
        tweet_df = pd.DataFrame(data=[self.clean_tweet(tweet.full_text) for tweet in tweets], columns=['tweets'])

        result = self.sentiment_tweet(tweet_df)

        #
        df = pd.DataFrame(result[0], columns=['polarity'])

        #
        df['sentiment'] = pd.DataFrame(result[1], columns=['sentiment'])

        #
        df['companies'] = pd.DataFrame(result[2], columns=['companies'])

        #
        new_df = self.to_df(df)

        return new_df

    '''
    extract the hashtag from tweets
    '''
    def hashtag_extract(self, tweets):
        hashtags = []
        # loop words in the tweet
        for tweet in tweets:
            ht = re.findall(r"#(\w+)", tweet)
            if(len(ht)):
                hashtags.append(ht)
        return hashtags

    '''
    convert to a new data frame
    to get rid of the tweets that didn't mention any companies
    '''
    def to_df(self, df):
        result_list = []
        item = []

        # iterate the data frame df
        for index, row in df.iterrows():
            if(row['companies'] != 'None'):
                item.append(row['companies'])
                item.append(row['sentiment'])
                result_list.append(item)
            item = []

        columns = ['company', 'sentiment']
        filtered_df = pd.DataFrame(result_list, columns = columns)

        return filtered_df


    '''
    return the positive sentiment value company
    '''
    def filter_positive(self, df):
        result_list = []
        item = []

        # iterate the data frame df
        for index, row in df.iterrows():
            if(row['companies'] != 'None' and (row['sentiment'] == 'wpositive'
                                               or row['sentiment'] == 'positive' 
                                               or row['sentiment'] == 'spositive')):
                item.append(row['companies'])
                item.append(row['sentiment'])
                result_list.append(item)
            item = []

        columns = ['company', 'sentiment']
        filtered_df = pd.DataFrame(result_list, columns = columns)

        return filtered_df

    '''
    Upload .csv files to Firebase Storage
    https://www.programcreek.com/python/example/120344/pandas.compat.BytesIO
    '''
    def upload_fire_base(self, df1, df2):

        firebase = pyrebase.initialize_app(config)
        storage = firebase.storage()

        #
        buf1 = BytesIO()
        str_buf1 = StringIO()

        df1.to_csv(str_buf1, index=False)

        buf1 = BytesIO(str_buf1.getvalue().encode('utf-8'))

        file1 = buf1

        path_on_cloud = self.get_account() + "/downloaded_tweets/" + self.get_filename() + ".csv"
        path_local = file1
        storage.child(path_on_cloud).put(path_local)


        #
        buf2 = BytesIO()
        str_buf2 = StringIO()

        df2.to_csv(str_buf2, index=False)

        buf2 = BytesIO(str_buf2.getvalue().encode('utf-8'))

        file2 = buf2

        path_on_cloud = self.get_account() + "/sentiment_data/" + self.get_filename() + "_sentiment" + ".csv"
        path_local = file2
        storage.child(path_on_cloud).put(path_local)

    '''
    doing the sentiment analysis of the tweets. It will categorized the tweets into group of positive, netural and negative
    '''
    def sentiment_tweet(self, df):
        
        tweets = df['tweets']

        sentiment_list = []
        polarity_list = []
        company_list = []

        # iterating through tweets fetched
        for tweet in tweets:

            # clean the junk message
            analysis = TextBlob(self.clean_tweet(tweet))

            companies = self.detect_companies(tweet)

            # neutral
            if (analysis.sentiment.polarity == 0):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('neutral')
                    company_list.append(companies[i])
            # wpositive
            elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('wpositive')
                    company_list.append(companies[i])
            # positive
            elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('positive')
                    company_list.append(companies[i])
            # spositive
            elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('spositive')
                    company_list.append(companies[i])
            # wnegative
            elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('wnegative')
                    company_list.append(companies[i])
            # negative
            elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('negative')
                    company_list.append(companies[i])
            # snegative
            elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                for i in range(0, len(companies)):
                    polarity_list.append(analysis.sentiment.polarity)
                    sentiment_list.append('snegative')
                    company_list.append(companies[i])

        return (polarity_list, sentiment_list, company_list)


    '''
    check if tweets contains any company's name from the dictionary fron company_list.py
    '''
    def detect_companies(self, tweet):
        
        company_names = companies.keys()
        stock_names = companies_stock_market.keys()

        # create an empty dictionary
        result = []

        # split each tweet into a list of words
        words = tweet.split()

        for word in words:
            if (word in company_names or word in stock_names):
                if(word not in result):
                    if(word in stock_names):
                        word = companies_stock_market[word]
                    result.append(word)

        return result