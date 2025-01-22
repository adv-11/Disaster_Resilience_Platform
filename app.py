import streamlit as st

dashboard = st.Page(
    page = "views/dashboard.py",
    title = "Dashboard",
    icon = "🏠",
    default = True
)

affected_areas = st.Page(
    page = "views/affected_areas.py",
    title = "Affected Areas",
    icon = "🌍"
)

visualizations = st.Page(
    page = "views/visualizations.py",
    title = "Visualizations",
    icon = "📊"
)

donations = st.Page(
    page = "views/donations.py",
    title = "Donations",
    icon = "💰"
)

chatbot = st.Page (
    page='views/chatbot.py',
    title="Resilio Chatbot", 
    icon="🤖"
)

st.set_page_config(layout="wide")
st._config.set_option(f'theme.base', "light")

#Navigation bar
pg = st.navigation(pages=[dashboard, donations, affected_areas, visualizations, chatbot])

st.sidebar.text("Navigation")

pg.run()


