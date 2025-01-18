import requests
import os 
from dotenv import load_dotenv
load_dotenv()

# News API credentials
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def fetch_web_data(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response.json()['articles']  # Extract articles from the response

# Example of fetching articles related to LA Wildfires
articles = fetch_web_data("LA Wildfires")
for article in articles:
    print(article['title'])
    print(article['content'])