import streamlit as st
import requests
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
import json
import re
import plotly.graph_objects as go
from dotenv import load_dotenv
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions
import pandas as pd

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

# Initialize IBM Watson NLU client
nlu_authenticator = IAMAuthenticator(NLU_API_KEY)
nlu = NaturalLanguageUnderstandingV1(
    version="2021-08-01",
    authenticator=nlu_authenticator
)
nlu.set_service_url(NLU_URL)

# Fetch real-time data using News API
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")


@st.cache_data
def fetch_web_data(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])
    return [(article["title"], article["content"]) for article in articles if article.get("content")]


# Function to clean HTML tags from the content
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


# Visualization Functions
def create_pie_chart(data, settings):
    categories = [item[settings["categoriesField"]] for item in data]
    values = [item[settings["valuesField"]] for item in data]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=values,
                hole=0.3,
                textinfo="label+percent",
                marker=dict(colors=["orange", "red", "blue", "green", "purple"])
            )
        ]
    )
    fig.update_layout(title="Pie Chart: Acres Burned by County")
    return fig


def create_multiseries_chart(data, settings):
    fig = go.Figure()

    for series in settings["multiSeriesFields"]:
        fig.add_trace(
            go.Bar(
                x=[item[settings["x"]] for item in data],
                y=[item[series["name"]] for item in data],
                name=series["name"]
            )
        )

    fig.update_layout(
        title="Multiseries Chart: Acres Burned by County",
        barmode="group",
        xaxis_title=settings["x"],
        yaxis_title="Value"
    )
    return fig


# Load visualization settings
with open("ibm_autoML_visualizations\chart_setting_pie.json", "r") as pie_file:
    pie_settings = json.load(pie_file)

with open("ibm_autoML_visualizations\chart_setting_multiseries.json", "r") as multiseries_file:
    multiseries_settings = json.load(multiseries_file)

# Sample data for visualization
# Load data from CSV file
data_file_path = "datasets\California_Fire_Incidents.csv"
data_df = pd.read_csv(data_file_path)

# Convert DataFrame to list of dictionaries
sample_data = data_df.to_dict(orient="records")

# Streamlit App Layout
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Donation Page", "Visualization"])

if page == "Donation Page":
    st.title("Disaster Relief Donation Platform")
    st.subheader("Contribute to make a difference!")

    # Donation form
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    amount = st.number_input("Donation Amount (USD)", min_value=1)
    comment = st.text_area("Your Message (Optional)")

    # Submit donation
    if st.button("Donate"):
        if name and email and amount > 0:
            try:
                donation_document = {
                    "name": name,
                    "email": email,
                    "amount": amount,
                    "comment": comment
                }
                client.post_document(db=CLOUDANT_DB_NAME, document=donation_document)
                st.success(f"Thank you, {name}! Your donation of ${amount} has been recorded.")
            except Exception as e:
                st.error(f"Error saving donation: {e}")
        else:
            st.error("Please fill in all required fields.")

elif page == "Dashboard":
    st.title("Dashboard")

    # Divide the page into 4 blocks
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # Block A: Donations Info
    with col2:
        st.write("### Donations")
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

    # Block B: Placeholder
    with col1:
        st.write("### Block B: Placeholder")

    # Block C: News Summary and Sentiment
    with col3:
        st.write("### LA Wildfires News Summary")

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

    # Block D: Placeholder
    with col4:
        st.write("### Block D: Placeholder")

elif page == "Visualization":
    st.title("Data Visualization")

    # Pie Chart Visualization
    st.subheader("Pie Chart: Acres Burned by County")
    pie_chart = create_pie_chart(sample_data, pie_settings)
    st.plotly_chart(pie_chart, use_container_width=True)

    # Multiseries Chart Visualization
    st.subheader("Multiseries Chart: Acres Burned by County")
    multiseries_chart = create_multiseries_chart(sample_data, multiseries_settings)
    st.plotly_chart(multiseries_chart, use_container_width=True)
