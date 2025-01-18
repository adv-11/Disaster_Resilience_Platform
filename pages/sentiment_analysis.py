import streamlit as st
from tavily import TavilyClient
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os 
from dotenv import load_dotenv
load_dotenv()
import requests

import plotly.graph_objects as go




# IBM Watson NLU Credentials
NLU_API_KEY = os.environ.get("NLU_API_KEY")
NLU_URL = os.environ.get("NLU_URL")

# Initialize IBM Watson NLU client
authenticator = IAMAuthenticator(NLU_API_KEY)
nlu = NaturalLanguageUnderstandingV1(
    version='2021-08-01',
    authenticator=authenticator
)
nlu.set_service_url(NLU_URL)

# init Tavily client
TAVILY_API_KEY = "tvly-YOUR_API_KEY"
tavily = TavilyClient(api_key=TAVILY_API_KEY)

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
def fetch_web_data(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return [article['content'] for article in articles if article.get('content')]

# Function to analyze sentiment using Watson NLU
def analyze_sentiment(text):
    try:
        response = nlu.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions())
        ).get_result()
        sentiment = response['sentiment']['document']['label']
        score = response['sentiment']['document']['score']
        return sentiment, score
    except Exception as e:
        st.error(f"Error analyzing sentiment: {e}")
        return None, None

# Streamlit App for Sentiment Analysis
st.title("Real-Time Sentiment Analysis of LA Wildfires")
st.subheader("Analyze the sentiment of recent data about LA Wildfires.")

# Step 1: Fetch real-time data using News API
query = "LA Wild Fires news"  # Modify the query to fetch relevant results
if st.button("Analyze LA Wildfires News"):
    # Fetch data using News API
    st.info("Fetching web data...")
    web_data = fetch_web_data(query)

    if web_data:
        st.success("Data fetched successfully!")
        st.write("### Web Data (Headlines/Articles)")
        st.write(web_data[:5])  # Display the first 5 items

        # Step 2: Perform sentiment analysis on each piece of fetched data
        st.write("### Sentiment Analysis Results")
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        sentiment_scores = []

        for i, text in enumerate(web_data[:5]):
            sentiment, score = analyze_sentiment(text)
            if sentiment:
                sentiment_scores.append(score)
                sentiment_counts[sentiment.lower()] += 1
                st.write(f"**Text {i + 1}:** {text}")
                st.write(f"- Sentiment: {sentiment.capitalize()} (Score: {score:.2f})")

        # Step 3: Visualize the sentiment results
        # Pie Chart showing sentiment distribution
        fig = go.Figure(data=[go.Pie(labels=list(sentiment_counts.keys()), 
                                     values=list(sentiment_counts.values()), 
                                     hole=0.4, 
                                     textinfo="label+percent")])
        fig.update_layout(title="Sentiment Distribution of LA Wildfires News")
        st.plotly_chart(fig, use_container_width=True)

        # Calculate and display the average sentiment score
        average_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        st.write(f"### Average Sentiment Score: {average_score:.2f}")

        # Display the overall sentiment summary
        if sentiment_counts['negative'] > sentiment_counts['positive']:
            overall_sentiment = "Negative"
        elif sentiment_counts['positive'] > sentiment_counts['negative']:
            overall_sentiment = "Positive"
        else:
            overall_sentiment = "Neutral"

        st.write(f"### Overall Sentiment: {overall_sentiment}")

    else:
        st.warning("No data found for the query.")