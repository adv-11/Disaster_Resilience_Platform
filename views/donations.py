import streamlit as st
import os
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


# IBM Cloudant Credentials
CLOUDANT_API_KEY = os.environ.get("CLOUDANT_API_KEY")
CLOUDANT_URL = os.environ.get("CLOUDANT_URL")
CLOUDANT_DB_NAME = os.environ.get("CLOUDANT_DB_NAME")
authenticator = IAMAuthenticator(CLOUDANT_API_KEY)
client = CloudantV1(authenticator=authenticator)
client.set_service_url(CLOUDANT_URL)


# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------- PAGE CONFIGURATION ---------------------------------------------

st.title("💰 Donations")
st.markdown("---")

# Donation form
name = st.text_input("Your Name")
email = st.text_input("Your Email")
amount = st.number_input("Donation Amount (USD)", min_value=1)
comment = st.text_area("Your Message (Optional)")

if st.button("Donate"):
    if name and email and amount > 0:
        try:
            donation_document = {
                "name": name,
                "email": email,
                "amunt": amount,
                    "comment": comment
            }
            client.post_document(db=CLOUDANT_DB_NAME, document=donation_document)
            st.success(f"Thank you, {name}! Your donation of ${amount} has been recorded.")
        except Exception as e:
            st.error(f"Error saving donation: {e}")
    else:
        st.error("Please fill in all required fields.")