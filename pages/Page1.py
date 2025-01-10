import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile

classes = []
# Firebase setup
firebase_credentials = dict(st.secrets["firebase"])

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("Previous Responses")

# Step 1: Fetch unique classes from Firestore
@st.cache_data
def get_unique_classes():
    classes = set()
    docs = db.collection("ai_responses").stream() #allows the program to iterate through every entry
    for doc in docs:
        data = doc.to_dict() #converts each entry to a dictionary which is readable by python
        classes.add(data["class"].lower()) #adds the class to the set
    return sorted(classes) #turns the set into a sorted list

classes = get_unique_classes()

# Step 2: Create a dropdown to select a class
if classes:
    selected_class = st.selectbox("Subjects", options=classes)
    
    # Step 3: Fetch responses for the selected class
    @st.cache_data
    def get_responses_by_class(selected_class):
        responses = []
        docs = db.collection("ai_responses").stream()
        for doc in docs:
            data = doc.to_dict()
            if data["class"].lower() == selected_class.lower():
                responses.append({
                    "Response": data.get("response", "N/A"),
                    "Timestamp": data.get("timestamp", "N/A"),
                })
        return responses

    responses = get_responses_by_class(selected_class)

    # Step 4: Display responses
    if responses:
        st.write(f"Responses for {selected_class}")
        for response in responses:
            time = (f"{response['Timestamp']}"[:10])
            st.markdown(f"**Date:**({time}) {response['Response']}")
else:
    st.warning("You haven't specified any subjects")