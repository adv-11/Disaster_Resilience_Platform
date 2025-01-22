import streamlit as st
import time
import firebase_admin
from firebase_admin import db, credentials
import pandas as pd
import folium
from streamlit_folium import st_folium

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred, {"databaseURL": "https://disaster-resilience-sos123-default-rtdb.firebaseio.com/"})

# Function to fetch SOS messages from Firebase Realtime Database
@st.cache_data()
def fetch_sos_data():
    ref = db.reference("SOSMessages")
    data = ref.get()
    if data:  # Check if data exists
        records = []
        for key, value in data.items():
            # Extract and store the relevant fields in a list of dictionaries
            records.append({
                "Latitude": float(value["Latitude"]),
                "Longitude": float(value["Longitude"]),
                "Message": value["Message"],
            })
        return pd.DataFrame(records)  # Convert the list of dictionaries to a DataFrame
    return pd.DataFrame(columns=["Latitude", "Longitude", "Message"])  # Return an empty DataFrame if no data


def plot_map(data):
    # Initialize a Folium map centered on the average coordinates
    m = folium.Map(location=[data["Latitude"].mean(), data["Longitude"].mean()], zoom_start=8)

    # Add markers for each SOS message
    for _, row in data.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"Message: {row['Message']}",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    return m


# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------- PAGE CONFIGURATION ---------------------------------------------

st.title("🚨 Real-time SOS Messages")
st.subheader('Real time SOS messages from the Android Application')
st.markdown("---")

# Fetch the latest SOS data from Firebase
sos_data = fetch_sos_data()

# Check if there is any data
if not sos_data.empty:
    st.subheader(f"Displaying {len(sos_data)} SOS Messages")
        
    # Plot the map with the fetched SOS data
    map_object = plot_map(sos_data)
        
    # Render the map in Streamlit using the streamlit_folium package
    st_folium(map_object, width="100%", height=500)
else:
    st.warning("No SOS Messages to display")

if st.button("Refresh Data"):
    st.rerun()


    