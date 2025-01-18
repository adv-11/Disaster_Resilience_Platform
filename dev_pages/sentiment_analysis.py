import streamlit as st
from tavily import TavilyClient
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, KeywordsOptions, EntitiesOptions
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

# Function to analyze text and extract keywords and entities
def analyze_summary(text):
    try:
        response = nlu.analyze(
            text=text,
            features=Features(
                keywords=KeywordsOptions(emotion=False, sentiment=False, limit=5),
                entities=EntitiesOptions(emotion=False, sentiment=False, limit=5)
            )
        ).get_result()
        
        keywords = [keyword['text'] for keyword in response['keywords']]
        entities = [entity['text'] for entity in response['entities']]
        
        # Constructing a summary from extracted keywords and entities
        summary = f"Key Entities: {', '.join(entities)}\nKey Topics: {', '.join(keywords)}"
        return summary
    except Exception as e:
        st.error(f"Error analyzing summary: {e}")
        return None

# Streamlit App for Summarizing LA Wildfires News
st.title("Summarize LA Wildfires News")
st.subheader("Generate a summary for recent news articles about LA Wildfires.")

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

        # Step 2: Perform summarization on each fetched article
        st.write("### Summarized Results")
        for i, text in enumerate(web_data[:5]):
            summary = analyze_summary(text)
            if summary:
                st.write(f"**Text {i + 1}:** {text[:150]}...")  # Display the first 150 characters
                st.write(f"- Summary: {summary}")
    else:
        st.warning("No data found for the query.")