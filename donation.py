import streamlit as st
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
import os

# IBM Cloudant Credentials
CLOUDANT_API_KEY = os.environ.get("CLOUDANT_API_KEY")
CLOUDANT_URL = os.environ.get("CLOUDANT_URL")
CLOUDANT_DB_NAME = os.environ.get("CLOUDANT_DB_NAME")


# init Cloudant client
authenticator = IAMAuthenticator(CLOUDANT_API_KEY)
client = CloudantV1(authenticator=authenticator)
client.set_service_url(CLOUDANT_URL)

#  create database if it doesn't exist
def create_database():
    try:
        put_database_result = client.put_database(db=CLOUDANT_DB_NAME).get_result()
        if put_database_result["ok"]:
            st.info(f'"{CLOUDANT_DB_NAME}" database created successfully.')
    except ApiException as ae:
        if ae.status_code == 412:
            st.info(f'Database "{CLOUDANT_DB_NAME}" already exists.')

#  save donation details
def save_donation(name, email, amount, comment):
    try:
        # Create a document for the donation
        donation_id = name.lower().replace(" ", "_") + "_donation"
        donation_document: Document = Document(
            id=donation_id,
            name=name,
            email=email,
            amount=amount,
            comment=comment,
            
        )
        # save  doc in the database
        create_document_response = client.post_document(
            db=CLOUDANT_DB_NAME,
            document=donation_document
        ).get_result()
        st.success("Thank you! Your donation has been recorded.")
    except ApiException as e:
        st.error(f"Failed to save donation: {e}")

# Streamlit 
st.title("Disaster Relief Donation Platform")
st.subheader("Contribute to make a difference!")

#  form
name = st.text_input("Your Name")
email = st.text_input("Your Email")
amount = st.number_input("Donation Amount (USD)", min_value=1)
comment = st.text_area("Your Message (Optional)")

# init Cloudant database
create_database()

# submit 
if st.button("Donate"):
    if name and email and amount > 0:
        save_donation(name, email, amount, comment)
    else:
        st.error("Please fill in all required fields.")
