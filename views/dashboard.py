import os
import time
import json
import streamlit as st
import folium
from streamlit_folium import st_folium
from views.affected_areas import download_geojson, fetch_disaster_data, filter_recent_entries, plot_disaster_events


# Dashboard Title
st.title("🏠 Dashboard")

# Split into sections
st.markdown("---")

col1, col2 = st.columns([1, 1])  # Top row
col3, col4 = st.columns([1, 1])  # Bottom row

# Section 1: Affected Areas (Top Left)
with col1:
    st.markdown("### 🌍 Affected Areas")
    m = folium.Map(location=[37.0902, -100.7129], zoom_start=3.5)

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
            
    st_folium(m, width="100%", height=500, key="dashboard_map")    

    if st.button("Learn More"):
        st.switch_page("views/affected_areas.py")

# Section 2: Latest News (Top Right)
with col2:
    st.markdown("### Donations")

# Section 3: Ongoing Fundraisers (Bottom Left)
with col3:
    st.markdown("### Latest News")

# Section 4: Contact Information (Bottom Right)
with col4:
    st.markdown("### 📞 NGO Contacts")