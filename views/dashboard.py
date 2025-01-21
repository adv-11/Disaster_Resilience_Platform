import os
import re
from dotenv import load_dotenv
import requests
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions
from views.affected_areas import download_geojson, fetch_disaster_data, filter_recent_entries, plot_disaster_events, get_latest_news

load_dotenv()

# IBM Cloudant Credentials
CLOUDANT_API_KEY = os.environ.get("CLOUDANT_API_KEY")
CLOUDANT_URL = os.environ.get("CLOUDANT_URL")
CLOUDANT_DB_NAME = os.environ.get("CLOUDANT_DB_NAME")
authenticator = IAMAuthenticator(CLOUDANT_API_KEY)
client = CloudantV1(authenticator=authenticator)
client.set_service_url(CLOUDANT_URL)

# IBM Watson NLU Credentials
NLU_API_KEY = os.environ.get("NLU_API_KEY")
NLU_URL = os.environ.get("NLU_URL")

# Fetch real-time data using News API
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

@st.cache_data
def fetch_web_data(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])
    return [(article["title"], article["content"]) for article in articles if article.get("content")]

# Initialize IBM Watson NLU client
nlu_authenticator = IAMAuthenticator(NLU_API_KEY)
nlu = NaturalLanguageUnderstandingV1(
    version="2021-08-01",
    authenticator=nlu_authenticator
)
nlu.set_service_url(NLU_URL)

# Function to create a donation pie chart
@st.cache_data
def fetch_donations():
    try:
        response = client.post_all_docs(
            db=CLOUDANT_DB_NAME,
            include_docs=True
        ).get_result()
        return [doc["doc"] for doc in response["rows"]]
    except Exception as e:
        st.error(f"Error fetching donation data: {e}")
        return []


# Calculate the total donation amount
def calculate_total_donations(donations):
    return sum(donation["amount"] for donation in donations if "amount" in donation)


# Create a pie chart for donation progress
def create_donation_pie_chart(total_donations, goal_amount):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Donations Raised", "Remaining to Goal"],
                values=[total_donations, max(0, goal_amount - total_donations)],
                hole=0.6,  # Donut chart
                marker=dict(colors=["blue", "lightgray"]),
                textinfo="label+percent"
            )
        ]
    )
    fig.update_layout(
        title_text="Donation Progress",
        showlegend=False
    )
    return fig


def clean_html(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)

# Function to analyze text and extract keywords
def analyze_summary(title, text):
    try:
        response = nlu.analyze(
            text=text,
            features=Features(
                keywords=KeywordsOptions(emotion=False, sentiment=False, limit=5)
            )
        ).get_result()

        keywords = [keyword["text"] for keyword in response["keywords"]]

        # Constructing a summary from title and extracted keywords
        summary = f"**{title}**\n\n**Key Topics**: {', '.join(keywords)}"

        return summary
    except Exception as e:
        st.error(f"Error analyzing summary: {e}")
        return None


# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------- PAGE CONFIGURATION ---------------------------------------------

st.title("🏠 Dashboard")
st.markdown("---")

# Split into sections
col1, col2 = st.columns([1, 1])  # Top row
col3, col4 = st.columns([1, 1])  # Bottom row

# Section 1: Affected Areas (Top Left)
with col1:
    st.header("🌍 Affected Areas")    
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

    

# Section 2: Donations (Top Right)
with col2:
    st.header("💰Donations")

    donations = fetch_donations()
    total_donations = calculate_total_donations(donations)
    goal_amount = 100

    fig = create_donation_pie_chart(total_donations, goal_amount)
    st.plotly_chart(fig, use_container_width=True)

    st.write(f"- **Total Donations Raised:** ${total_donations}")
    st.write(f"- **Goal Amount:** ${goal_amount}")
    st.write(f"- **Number of Donations:** {len(donations)}")
    st.write(f"- **Goal Achieved:** {total_donations / goal_amount:.2%}")
    st.write(f"- **Top Donor:** {max(donations, key=lambda x: x['amount'])['name'] if donations else 'N/A'}")

    
    

# Section 3: Latest News (Bottom Left)
with col3:
    st.header("📰 LA Wildfires News Summary")
    
    query = "LA Wild Fires"
    st.info("Fetching and summarizing LA Wildfires news...")
    web_data = fetch_web_data(query)

    if web_data:
        st.success("Data fetched successfully!")
        for i, (title, content) in enumerate(web_data[:5]):
            cleaned_text = clean_html(content)
            summary = analyze_summary(title, cleaned_text)

            if summary:
                st.write(f"Headline {i + 1}:")
                st.write(f"- {summary}")
    else:
        st.warning("No data found for the query.")

    #Button for more news updates
    address = st.text_input("Enter your address for more news updates:")

    if st.button("Get Latest News"):
        if address:
            st.session_state.address = address
            st.session_state.more_news_articles = get_latest_news(f"Latest news in {address}")
            st.session_state.more_news_count = 3

    if 'address' in st.session_state and 'more_news_articles' in st.session_state:
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
            st.error("No news articles found for the given address.")
        
    

# Section 4: Contact Information (Bottom Right)
with col4:
    st.header("📞 Emergengy Contacts")

    st.write("""
    - **Fire Department (LAFD):** (213) 978-3800  
    Description: General fire safety and emergencies  

    - **Emergency Helpline:** 911  
    Description: Immediate assistance for emergencies  

    - **Red Cross Hotline:** (800) 733-2767  
    Description: Support and disaster assistance  

    - **LA County Helpline:** 211  
    Description: Local disaster resources and info  

    - **Animal Services:** (888) 452-7381  
    Description: Assistance for pets and livestock  

    - **FEMA Helpline:** (800) 621-3362  
    Description: Federal disaster relief and support  

    - **Volunteer LA Hotline:** (213) 347-3100  
    Description: Opportunities for volunteering  
    """)
        