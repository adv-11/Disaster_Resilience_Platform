# Disaster Resilience Platform

Problem Statement :
Natural disasters such as floods, hurricanes, etc cause significant damage to life, property, and infrastructure.​

A major challenge during disasters is the lack of real-time communication, effective coordination, and actionable insights for rescue teams, governments, and affected individuals. ​

During disasters, donations are often mismanaged or lack transparency, causing mistrust and inefficiency. ​

An AI-powered disaster management platform is needed to identify disasters and assess risk zones, coordinate rescue and relief efforts in real-time, and provide post-disaster recovery assistance.​

## Documentation

### Overview

Project for the IBM Skills Build Hackathon

<br>

The Disaster Resilience Platform is a web application designed to provide real-time information and analysis on various disaster-related topics. It includes features such as a dashboard, affected areas visualization, donation tracking, visualizations, a chatbot, and SOS messages.

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/adv-11/Disaster_Resilience_Platform.git
   cd Disaster_Resilience_Platform
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a [.env](http://_vscodecontentref_/1) file in the root directory of the project and add the following variables:

   ```env

    WATSON_API_KEY = ""

    NEWS_API_KEY= ""
    CLOUDANT_API_KEY = ""
    CLOUDANT_URL = ""
    CLOUDANT_DB_NAME = ""
    TAVILY_API_KEY = ""
    NLU_API_KEY = ""
    NLU_URL = ""

    TWITTER_API_KEY = ""

    TWITTER_API_SECRET =' '

    TWITTER_BEARER_TOKEN = ''

    TWITTER_ACCESS_TOKEN = ''

    TWITTER_ACCESS_TOKEN_SECRET = ''

    NASA_API_KEY = ''

    # for watson granite models

    apikey = ''

    watson_url = ''

    project_id = ''

    HF_TOKEN = ''
   ```

### Running the Application

5. **Run the Streamlit application:**
   ```sh
   streamlit run app.py
   ```

### Project Structure

- **app.py**: The main entry point of the application. It sets up the navigation and page configuration.

- **views/dashboard.py**: Contains the code for the dashboard page, which provides an overview of the disaster-related data.
- **views/affected_areas.py**: Contains the code for visualizing affected areas using GeoJSON data.
- **views/visualizations.py**: Contains various visualizations related to disaster data.
- **views/donations.py**: Tracks and displays donation information.
- **views/chatbot.py**: Implements a chatbot for user interaction.
- **views/sos.py**: Displays SOS messages and related information.

### Purpose of Each Python File

- **dashboard.py**: Provides a summary and key metrics related to disasters.
- **affected_areas.py**: Downloads and visualizes GeoJSON data to show affected areas.
- **visualizations.py**: Generates charts and graphs to visualize disaster data.
- **donations.py**: Manages and displays information about donations.
- **chatbot.py**: Implements a chatbot to assist users with queries.
- **sos.py**: Displays emergency SOS messages and alerts taken from mobile devices of users.

### IBM Technologies Used

- **IBM IAM**
- **IBM Cloudant**
- **IBM Secrets Manager**
- **Natural Language Understanding**
- **IBM Watsonx.ai Studio**
- **IBM Watsonx.ai Runtime**
- **IBM Watsonx.ai Assistant**
- **IBM Internet Services**
- **IBM Cloud Object Storage**
- **IBM AutoML**
- **IBM Event Notifications**

### Additional Information

For more details, please refer to the individual Python files and their respective comments and documentation.

---

Feel free to contribute to this project by submitting issues or pull requests. For any questions, please contact the project contributors.
