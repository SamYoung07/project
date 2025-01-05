import PIL.Image
from PIL import Image
import google.generativeai as genai
import pillow_heif
import streamlit as st
from io import BytesIO
import datetime

st.title("PINPOINT AI")
st.write("Your personal AI notetaking assistant")

pillow_heif.register_heif_opener()

def convert_heic_to_jpeg(input_stream, output_path):
    # Open HEIC file from the stream
    heic_image = Image.open(input_stream)
    # Save as JPEG
    heic_image.save(output_path, "JPEG")
    print(f"Converted HEIC to {output_path}")

api_key = st.secrets["default"]["API_KEY"]

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Upload File section
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file:
    file_name = uploaded_file.name

# Button Options
left, middle, right = st.columns(3)
summary = left.checkbox("Summary")
notes = middle.checkbox("Extra Notes")
practice = right.checkbox("Practice Questions")

# Run Button
options = []
prompts = ["With the given image, create: "]
if st.button("RUN", type="primary"):
    if summary:
        options.append("- Summary")
        prompts.append("A brief summary of what the image says,")
    if notes:
        options.append("- Extra Notes")
        prompts.append(" 3 extra notes (one sentence each) about the topic covered in the image, ")
    if practice:
        options.append("- Practice Questions")
        prompts.append(" 2 Practice questions related to the topic.")
    st.write("Creating: ")
    for i in options:
        st.write(i)

    # AI CODE
    if uploaded_file:
        filetype = file_name.split('.')[-1].lower() #takes last index of the list created from the split string (heic or jpg)
        if filetype == 'heic':
            # Convert HEIC to JPEG
            new_file_name = file_name.replace('.heic', '.jpg')
            convert_heic_to_jpeg(uploaded_file, new_file_name)
            img = PIL.Image.open(new_file_name)
        else:
            # Open other file types directly
            img = PIL.Image.open(uploaded_file)

        # Append image and generate response
        prompts.append(img)
        response = model.generate_content(prompts)
        assistant = response.text
        st.write(assistant)
    else:
        st.error("No file uploaded.")