import tweepy
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
from dotenv import load_dotenv
load_dotenv()


twitter_api_key = os.environ.get("TWITTER_API_KEY")
twitter_api_secret = os.environ.get("TWITTER_API_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

# Set up Tweepy client
auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Function to fetch tweets related to LA Wildfires
def fetch_tweets(query):
    
    # Use the search_tweets method in Tweepy v4.x
    tweets = api.search_tweets(q=query, count=10, lang="en", tweet_mode='extended')
    return [tweet.full_text for tweet in tweets]
    
    
result = fetch_tweets("LA Wildfires")
for tweet in result:
    print(tweet)