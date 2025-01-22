import requests
import streamlit as st
import time
import folium
import json
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY") or st.secrets["NEWS_API_KEY"]

# Function to download the latest GeoJSON file using Selenium
@st.cache_data
def download_geojson(url, download_dir):
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_dir}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    # Execute the JavaScript to download the file
    driver.execute_script("downloadResult();")
    
    # Wait for the download to complete
    time.sleep(10)
    
    driver.quit()

# Function to fetch disaster data from a GeoJSON file
def fetch_disaster_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

# Function to filter entries from the last 3 months
@st.cache_data
def filter_recent_entries(entries, months=3):
    recent_entries = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=months*30)  # Approximate 3 months
    for entry in entries:
        if 'fromdate' in entry['properties']:
            entry_date = datetime.strptime(entry['properties']['fromdate'], '%Y-%m-%dT%H:%M:%S')
            if entry_date >= cutoff_date:
                recent_entries.append(entry)
    return recent_entries

def plot_disaster_events(m, disaster_data):
    for event in disaster_data:
        properties = event['properties']
        geometry = event['geometry']
        if geometry['type'] == 'Point':
            lat, lon = geometry['coordinates'][1], geometry['coordinates'][0]
            title = properties['eventname']
            description = properties['description']
            fromdate = properties['fromdate']
            more_info_url = properties['url'].get('report', None)
            if more_info_url:
                popup_text = f"{title}: {description}<br>Date: {fromdate}<br><a href='{more_info_url}' target='_blank'>More Info</a>"
            else:
                popup_text = f"{title}: {description}<br>Date: {fromdate}"
            folium.Marker([lat, lon], popup=popup_text).add_to(m)     

# Function to get latest news about California fires

@st.cache_data
def get_latest_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    return news_data['articles']
      


# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------- PAGE CONFIGURATION ---------------------------------------------

st.title("🗺️ Global Disaster Affected Areas")
st.markdown("---")

m = folium.Map(location=[20.0, 0.0], zoom_start=2)

# Download the latest GeoJSON file if it doesn't exist
geojson_url = "https://www.gdacs.org/Alerts/default.aspx"
download_dir = os.getcwd()  # Current working directory
geojson_filepath = os.path.join(download_dir, "result.geojson")
if not os.path.exists(geojson_filepath):
    download_geojson(geojson_url, download_dir)

# Fetch disaster data from GeoJSON file
disaster_data = fetch_disaster_data(geojson_filepath)
if 'features' in disaster_data:
    recent_disaster_data = filter_recent_entries(disaster_data['features'])
    plot_disaster_events(m, recent_disaster_data)    
else:
    st.error("No disaster events found") 
        
st_folium(m, width="100%", height=500 , key="affected_areas_map")



#Fetch latest news about California fires
st.markdown("---")
st.markdown("### 📰 Latest News About California Fires")

st.info("Fetching and summarizing LA Wildfires news...")

news_articles = get_latest_news("California fires")

if 'news_count' not in st.session_state:
    st.session_state.news_count = 3

if news_articles:
    st.success("News fetched successfully!")
    for article in news_articles[:st.session_state.news_count]:
        title = article['title']
        description = article['description']
        url = article['url']
        st.markdown(f"- [{title}]({url})")
        st.write(description)

    if len(news_articles) > st.session_state.news_count:
        if st.button("See more"):
            st.session_state.news_count += 3
            st.rerun()



# Search for more news
st.markdown("---")
query = st.text_input("Search for more news:")

if st.button("Search"):
    if query:
        st.session_state.query = query
        st.session_state.more_news_articles = get_latest_news(query)
        st.session_state.more_news_count = 3

if 'query' in st.session_state and 'more_news_articles' in st.session_state:
    more_news_articles = st.session_state.more_news_articles
    if more_news_articles:
        st.success("News fetched successfully!")
        for article in more_news_articles[:st.session_state.more_news_count]:
            title = article['title']
            description = article['description']
            url = article['url']
            st.markdown(f"- [{title}]({url})")
            st.write(description)

        if len(more_news_articles) > st.session_state.more_news_count:
            if st.button("See more", key="more_news"):
                st.session_state.more_news_count += 3
                st.rerun()
    else:
        st.error("No news articles found for the given query.")





