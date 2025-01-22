import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json

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
with open("ibm_autoML_visualizations/chart_setting_pie.json", "r") as pie_file:
    pie_settings = json.load(pie_file)

with open("ibm_autoML_visualizations/chart_setting_multiseries.json", "r") as multiseries_file:
    multiseries_settings = json.load(multiseries_file)

with open("ibm_autoML_visualizations/chart_setting_multiseries_2.json", "r") as multiseries_file_1:
    multiseries_settings_1 = json.load(multiseries_file_1)

with open ("ibm_autoML_visualizations/chart_setting_pie_fuel_path.json", "r") as pie_file:
    pie_settings_fuel_path = json.load(pie_file)

# Sample data for visualization
# Load data from CSV file
data_file_path = "datasets/California_Fire_Incidents.csv"
data_df = pd.read_csv(data_file_path)

# Convert DataFrame to list of dictionaries
sample_data = data_df.to_dict(orient="records")

# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------- PAGE CONFIGURATION ---------------------------------------------

st.title("📊 Visualizations")
st.markdown("---")



# Pie Chart Visualization
st.header("Pie Chart: Acres Burned by County")
pie_chart = create_pie_chart(sample_data, pie_settings)
st.plotly_chart(pie_chart, use_container_width=True)

# Multiseries Chart Visualization
st.header("Multiseries Chart: Acres Burned by County")
multiseries_chart = create_multiseries_chart(sample_data, multiseries_settings)
st.plotly_chart(multiseries_chart, use_container_width=True)

# Additional Multiseries Chart Visualization
st.header("Multiseries Chart: Injuries and Crew Involved")
multiseries_chart_1 = create_multiseries_chart(sample_data, multiseries_settings_1)
st.plotly_chart(multiseries_chart_1, use_container_width=True)
