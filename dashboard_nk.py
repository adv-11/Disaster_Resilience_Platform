import os
import time
import json
import streamlit as st
import folium
from streamlit_folium import st_folium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

# Function to download the latest GeoJSON file using Selenium
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

# Set up the page layout
st.set_page_config(page_title="Global Disasters Dashboard", layout="wide")

# Dashboard Title
st.title("🌎 Global Disasters Dashboard")

# Split into sections
st.markdown("---")

col1, col2 = st.columns([1, 1])  # Top row
col3, col4 = st.columns([1, 1])  # Bottom row

# Section 1: Affected Areas (Top Left)
with col1:
    st.markdown("### 🗺️ Global Affected Areas & Disasters")
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

        for event in recent_disaster_data:
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
    else:
        st.error("No disaster events found")

    st_folium(m, width=700, height=500)

# Section 2: Latest News (Top Right)
with col2:
    st.markdown("### 📰 Latest News About Global Disasters")
    # Simulated news articles
    st.markdown("- [Disaster Spreads to New Areas](https://example.com)")
    st.markdown("- [Emergency Shelters Open for Disaster Victims](https://example.com)")
    st.markdown("- [Governor Declares State of Emergency](https://example.com)")
    st.markdown("- [How to Protect Your Home from Disasters](https://example.com)")

# Section 3: Ongoing Fundraisers (Bottom Left)
with col3:
    st.markdown("### 💰 Ongoing Fundraisers")
    # Fundraiser 1
    st.write("#### Disaster Relief Fund")
    progress = 500000 / 1000000  # Amount raised divided by goal
    st.progress(progress)
    st.write(f"Raised: $500,000 of $1,000,000")

# Section 4: Contact Information (Bottom Right)
with col4:
    st.markdown("### 📞 Contact Information")
    st.write("- Red Cross: (123) 456-7890")
    st.write("- Disaster Relief Fund: (987) 654-3210")