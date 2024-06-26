import streamlit as st
import os
import base64

# Define the path to your chatbot icon image
file_path = "robert.jpeg"

# Check if the file exists
if os.path.isfile(file_path):
    # Read and encode the image to base64
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    # Inject CSS to center the image
    st.sidebar.markdown(
        """
        <style>
        .centered-image {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Display the image in the sidebar
    st.sidebar.markdown(
        f'<div class="centered-image"><img src="data:image/png;base64,{encoded_image}" width="100"></div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.write("Chatbot icon not found")
