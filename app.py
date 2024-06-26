import streamlit as st
from src.UIPages.home_page import Conversation
from src.UIPages.insights_page import Insights
from src.UIPages.education_page import Education
from src.UIPages.alerts_page import AlertsPage
from streamlit_extras.colored_header import colored_header
st.set_page_config(layout="wide")
# Function to navigate to different pages

conv = Conversation('Hi my name Robert. Welcome to FinThrivin. How are you doing?')
insights = Insights()
education = Education()

if "user_id" not in st.session_state:
    st.session_state.user_id=None

def navigate_to_page(page):
    st.session_state.page = page

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def get_insights():
    with st.sidebar.container():
        st.title("Educational knowledge")
        user_input = st.sidebar.chat_input("type your question here")

def talk_to_robert():
    # print('main app repeating')
    conv.start_conversation()

# Define the content of each page
def home_page():
    "------------------------------------------------------------"
    st.header('FinThrivin', divider="rainbow")
    # st.write("<Financial health dashboard here>")
    st.markdown("<h1 style='text-align: center; color: black;'>Financial Health Dashboard</h1>", unsafe_allow_html=True)
    conv.start_conversation()
    # talk_to_robert()

def insights_page():
    #st.write("<insights and educational recomendations here>")
    #get_insights()
    insights.load_insights()


def alerts_page():
    if st.session_state.user_id != None:
        AlertsPage().render_alerts_page(int(st.session_state.user_id))

# st.title("FinThrivin")
def education_page():
    "------------------------------------------------------------"
    st.header('FinThrivin', divider="rainbow")
    # st.write("<Financial health dashboard here>")
    #st.markdown("<h1 style='text-align: center; color: black;'>Educational Articles</h1>", unsafe_allow_html=True)
    #st.write("<Alerts list here>")
    education.load_education()
    
with st.container():
    st.markdown(
        """
            <style>
            .custom-column {
                padding: 10px 10px; /* Adjust the padding as needed */
            }
            </style>
        """,
        unsafe_allow_html=True
        )
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        if st.session_state.user_id != None:
            st.write(f"<h5 style='font-size:18px;'>Hello {st.session_state.primary_details[0]}..!</h5>", unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home", key='home_button'):
            navigate_to_page('Home')
    with col3:
        if st.button("💡 Insights", key='Insights_button'):
            navigate_to_page('Insights')
    with col4:
        if st.button("🔔 Alerts", key='Alerts_button'):
            navigate_to_page('Alerts')
    with col5:
        if st.button("🔎 Education", key='Education_button'):
            navigate_to_page('Education')

# Render the current page based on the session state
if st.session_state.page == 'Home':
    home_page()
elif st.session_state.page == 'Insights':
    insights_page()
elif st.session_state.page == 'Alerts':
    alerts_page()
elif st.session_state.page == 'Education':
    education_page()
