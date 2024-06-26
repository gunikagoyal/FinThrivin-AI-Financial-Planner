
import streamlit as st
from PIL import Image
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
CURR_DIR = Path(__file__).resolve().parent
PARENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PARENT_DIR))
from db_utils import DbUtils
import math
# from finagent.main import Chatbot
from finance_planner_crew.educational_main import Chatbot
from streamlit_chat import message

# Initialize the Chatbot
chatbot = Chatbot()

# Explicitly specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Define custom emojis
# Define custom emojis using Unicode escape sequences
user_emoji = "\U0001F642"  
bot_emoji = "\U0001F916"  
    
class Education():
   def load_education(self):
        st.header('Educational Support:mag_right:')
        #container for chat history
        response_container = st.container()
        #container for text box
        textcontainer = st.container()
        # Initialize session state variables
        if 'requests' not in st.session_state:
            st.session_state.requests = []
        if 'responses' not in st.session_state:
            st.session_state.responses = []


        # Add a text input field for both speech and text queries
        # Add a text input field for both speech and text queries
        with textcontainer:
            # Add a text input field for query
            query = st.text_input("Query: ", key="input")

            # Process the query if it's not empty
            if query:
                with st.spinner("typing, please wait for a while....."):
                    # Context can be dynamically set based on the conversation flow
                    context = None

                    # Process user input with the Chatbot class
                    answer = chatbot.run_finagent(query, context)
                    
                    # Append the query and response to session state
                    st.session_state.requests.append(query)
                    st.session_state.responses.append(answer)
            


        # Display the chat history and response
        with response_container:
            if st.session_state['responses']:
                for i in range(len(st.session_state['responses'])):
                    message(f"{user_emoji} {st.session_state['requests'][i]}", key=str(i))
                    if i < len(st.session_state['requests']):
                        message(f"{bot_emoji} {st.session_state['responses'][i]}", is_user=True, key=str(i) + '_user')
      
       


                                                          
                                  
                
       

                    

                                    
    
        