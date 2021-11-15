# Stock Market Analysis
## Objective
- This project will predict a stock market by analyzing the tweets from twitter. It uses twitter API called Tweepy to download the data. After the data cleaning, it will utilize the concept of Sentiment Analysis to determine which tweets are positive and negative. It uses machine learning algorithm to understand the patten of the sentiment data and then predict the stock condition of the companies.

## There are there are three majority of parts in this project: Tweets Donloader, Stock Checker and Company Predicter 
- The downloaded tweets are saved in [Google Firebase](https://firebase.google.com/)
- Stock Checker will check if companies' stock info can be downloaded via Yahoo Finance API
- Company Predicter is done by doing the machine leaning from the sentiment data of tweets

## Tweets Donloader Deployment:
- It is currently deplyed in flask app though [pythonanywhere](https://www.pythonanywhere.com/).
