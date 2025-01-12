# PINPOINT

import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile
import PIL.Image
from PIL import Image
import google.generativeai as genai
import pillow_heif
import streamlit as st
from io import BytesIO

st.set_page_config(page_title = "PINPOINT", page_icon="📌")

st.title("PINPOINT")
st.write("Your personal AI notetaking assistant")
subject = st.text_input("What class is this for? ")

# Firebase setup
firebase_credentials = dict(st.secrets["firebase"])

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
db = firestore.client()

pillow_heif.register_heif_opener()

def convert_heic_to_jpeg(input_stream, output_path):
    # Open HEIC file from the stream
    heic_image = Image.open(input_stream)
    # Save as JPEG
    heic_image.save(output_path, "JPEG")
    print(f"Converted HEIC to {output_path}")

#AI Setup
api_key = st.secrets["default"]["API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Upload File section
uploaded_file = st.file_uploader("Upload an image")
if uploaded_file:
    file_name = uploaded_file.name
    left, middle, right = st.columns(3)
    middle.image(uploaded_file, width = 5000)

# Button Options
left, middle, right = st.columns(3)
summary = left.checkbox("Summary")
notes = middle.checkbox("Extra Notes")
practice = right.checkbox("Practice Questions")

# Run Button
options = []
prompts = ["With the given image, create: "]
if st.button("RUN", type="primary") and (summary or notes or practice):
    if summary:
        options.append("- Summary")
        prompts.append("A brief summary of the information covered in the image,")
    if notes:
        options.append("- Extra Notes")
        prompts.append(" 3 extra notes (one sentence each) related to the topic that weren't included, ")
    if practice:
        options.append("- Practice Questions")
        prompts.append(" 2 Practice questions related to the topic.")
    st.write("Creating: ")
    for i in options:
        st.write(i)

    if uploaded_file:
        filetype = file_name.split('.')[-1].lower() # Takes last index of the list created from the split string (heic or jpg)
        if filetype == 'heic':
            # Convert HEIC to JPEG
            new_file_name = file_name.replace('.heic', '.jpg')
            convert_heic_to_jpeg(uploaded_file, new_file_name)
            img = PIL.Image.open(new_file_name)
        else:
            img = PIL.Image.open(uploaded_file)

        # Append image and generate response
        prompts.append(img)
        response = model.generate_content(prompts)
        chat = response.text
        st.write(chat)

        # Save to Firestore if a subject is specified
        if subject: 
            doc_ref = db.collection("ai_responses").add({
                "file_name": file_name,
                "response": chat,
                "class" : subject,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

    else:
        st.error("No file uploaded.")

#Next Steps
# Add a second page to access previous chats
# This page will display all classes
# You can click on a class to see all response with the same class