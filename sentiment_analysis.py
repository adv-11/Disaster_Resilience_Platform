import streamlit as st
from tavily import TavilyClient
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os 
from dotenv import load_dotenv
load_dotenv()

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

# Initialize Tavily client
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
client = TavilyClient(api_key=TAVILY_API_KEY)

# Function to fetch web data using Tavily
def fetch_web_data(query):
    try:
        response = client.search(query, max_results=20)
        # Extracting the text content from search results (usually 'text' is in the response)
        search_results = []
        for result in response.get('data', []):
            search_results.append(result.get('text', ''))
        return search_results
    except Exception as e:
        st.error(f"Error fetching web data: {e}")
        return []

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

# Step 1: Fetch real-time data using Tavily search
query = "LA Wild Fires news"  # Modify the query to fetch relevant results
if st.button("Analyze LA Wildfires News"):
    # Fetch data using Tavily search
    st.info("Fetching web data...")
    web_data = fetch_web_data(query)

    if web_data:
        st.success("Data fetched successfully!")
        st.write("### Web Data (Headlines/Articles)")
        st.write(web_data[:5])  # Display the first 5 items

        # Step 2: Perform sentiment analysis on each piece of fetched data
        st.write("### Sentiment Analysis Results")
        for i, text in enumerate(web_data[:5]):
            sentiment, score = analyze_sentiment(text)
            if sentiment:
                st.write(f"**Text {i + 1}:** {text}")
                st.write(f"- Sentiment: {sentiment.capitalize()} (Score: {score:.2f})")
    else:
        st.warning("No data found for the query.")
