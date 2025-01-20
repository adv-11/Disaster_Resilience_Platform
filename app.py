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

st.set_page_config(layout="wide")

#Navigation bar
pg = st.navigation(pages=[dashboard, donations, affected_areas, visualizations])
pg.run()


