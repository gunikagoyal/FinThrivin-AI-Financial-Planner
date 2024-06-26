from pathlib import Path
import sys
CURR_DIR = Path(__file__).resolve().parent
PARENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PARENT_DIR))
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from user_questionnaire.user_questions import questions
from db_utils import DbUtils
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
import json

class Conversation(DbUtils):
    def __init__(self,question):
        super().__init__()
        self.primary_details = []
        self.user_id=None
        self.que = None
        self.question=question
        self.step=0
    
    def detect_yes_no(self,response):
        load_dotenv(find_dotenv())
        api_token = os.environ['HUGGINGFACEHUB_API_TOKEN']
        api_url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
        headers = {"Authorization": f"Bearer {api_token}"}
        payload = {"inputs": response}

        response = requests.post(api_url, headers=headers, json=payload)
        result = response.json()

        if not response.ok:
            raise Exception(f"Error: {result}")
        
        # print(result)

        label = result[0][0]['label']
        score = result[0][0]['score']
        
        # Map the sentiment to "yes" or "no"
        if label == 'POSITIVE':
            return 'yes', score
        else:
            return 'no', score

    def select_next_question(self,user_response, followups, store_data,decision, function_call,table_info):
        """this is to select next question in the queue"""

        # print(f"Current question :{self.que}")
        # print(f'user response : {user_response}')
        # print(f'store_data {store_data}')
        # print(f'decision {decision}')
        # print(f'function_call {function_call}')
        
        user_intension=''
        if store_data:
            # print(f"store information called{table_info[0]}-->{table_info[1]}--{user_response}")
            self.update_record(table_info[0],table_info[1],user_response,st.session_state.user_id )
            # store_information(table_info,user_response)
        if decision and function_call != None:
            if function_call.lower()=='verify_user'.lower():
                # print(f'primary details {st.session_state.primary_details}')
                user_intension, st.session_state.user_id=self.verify_user(st.session_state.primary_details)
                # print(f'is it new user ? {user_intension}')

            elif function_call.lower()=='sentiment_analysis'.lower():
                user_intension, confidence = self.detect_yes_no(user_response)
        if function_call != None:
            if function_call.lower()=='primary'.lower():
                st.session_state.primary_details.append(user_response)
            elif function_call.lower()=='create_profile'.lower():
                st.session_state.user_id = self.create_profile(st.session_state.primary_details)

        if user_intension.lower()=="No".lower():
            # print(f'followup question = {followups[1]}')
            return followups[1]
        else:
            # print(f'followup question = {followups[0]}')
            return followups[0]

    def start_conversation(self):
        """ this is the conversational chatbot in home page"""
        # colored_header(label='', description='', color_name='blue-green-70')
        welcome_msg = 'Hi my name Robert. Welcome to FinThrivin. How are you doing?'

        if "primary_details" not in st.session_state: 
            st.session_state.primary_details=[]

        if "current_question" not in st.session_state:
            st.session_state.current_question = self.question

        if "user_id" not in st.session_state:
            st.session_state.user_id = None

        if "conversation" not in st.session_state:
            st.session_state.conversation = [{'type': 'chatbot', 'text': welcome_msg}]
        
        st.sidebar.image(os.path.join(CURR_DIR,"robert.jpeg"), caption="Hello, this is Smith, How can I help you today?", use_column_width=True)
        # st.sidebar.title('User profile chatbot')

        for item in st.session_state.conversation:
            if item['type'] == 'user':
                # message(item['text'], is_user=True)
                st.sidebar.write("User Response older:", item['text'])
            else:
                # message(item['text'])
                st.sidebar.write("chatbot Response older:", item['text'])

        if st.session_state.user_id != None:
            self.financial_health_board(str(st.session_state.user_id))
        #     st.write(f"USER ID: {st.session_state.user_id}")
            # globals.USER_ID = st.session_state.user_id
        user_input_container = st.sidebar.container()
        # user_input_container.title('User profile chatbot')

        with user_input_container:
            
            
            try:
                user_input = st.chat_input("type your answer here",key=f"chat_input_{self.step}")
                self.step +=1
                if user_input:
                    st.session_state.conversation.append({'type': 'user', 'text': user_input})
                    # st.write("chatbot Response:", question)
                    current_question_key = st.session_state.current_question
                    item = questions[current_question_key]
                    self.que = item
                    followups = item['follow-up-questions']
                    store_info = item['store-information']
                    decision = item['decision']
                    func = item['function_call']
                    table_info=item['table_info']
                    next_question = self.select_next_question(user_input,followups,store_info,decision,func, table_info)
                    st.write("robert's response:", next_question)
                    st.session_state.conversation.append({'type': 'chatbot', 'text': next_question})
                    st.session_state.current_question = next_question
            except KeyError as keyerror:
                print('Thank you for your time.')
            except Exception as e:
                print(f'error ==== {e}')

    def financial_health_board(self, user_id):
        # Read user.csv file to obtain total income
        user_data = self.get_data1(
            table1='user',
            columns=['user_id','fixed_income_monthly', 'extra_income_monthly'],
            user_id=user_id  # Assuming user_id is the column for filtering
            # table2='',  # No second table needed
        )
        print('user data here====',user_data.head())
        # user_row = user_data[user_data['user_id'] == user_id]
        # user_row = user_data[user_data['user_id'].astype(str).str.contains(user_id)]
        fixed_income = user_data['fixed_income_monthly'].values[0]
        extra_income = user_data['extra_income_monthly'].values[0]
        total_income = fixed_income + extra_income
        # print(f'here is user data - {user_data}')
        # Obtain total_income from user.csv
        month = datetime.now().month
        year = datetime.now().year
        output_file = self.rename_csv_columns('fixed_expenses.csv','payment_due_date','date','expense_type','transaction_description')
        desired_columns = ["user_id", "transaction_description", "date", "amount"]
        # user_id='374576'
        combined_expenses = self.merge_data('converted_fixed_expenses', 'variable_expenses',desired_columns)
        print(combined_expenses.head(),'combined data is here =====')
        # combined_expenses['date'] = pd.to_datetime(combined_expenses['date'], format='%m/%d/%Y',errors='coerce')
        # current_date = datetime.now()

        # # Calculate the first day of the current month
        # first_day_current_month = current_date.replace(day=1)

        # # Calculate the first day of the previous month
        # first_day_previous_month = (first_day_current_month - timedelta(days=1)).replace(day=1)

        # # Calculate the last day of the previous month
        # # last_day_previous_month = first_day_current_month - timedelta(days=1)

        # filtered_df = combined_expenses[(combined_expenses['date']>= first_day_previous_month) & (combined_expenses['date'] <= current_date)]
        output_path = os.path.join(self.data_path, "transactions.csv")
        combined_expenses.to_csv(output_path, index=False)
        # Calculate the total expenses
        total_spendings = combined_expenses['amount'].sum()
        
        # Calculate Net Income
        net_income=total_income-total_spendings
        # Calculate Net Worth
        savings_data = self.get_data1(
            table1='savings',
            columns=['savings_amount'],
            user_id=user_id  # Assuming user_id is the column for filtering
            # table2='',  # No second table needed
        )
        total_savings_amount=savings_data['savings_amount'].sum()
        net_worth=net_income+total_savings_amount

        # Obtain forecasted expenses for the user
        file_path=os.path.join(self.data_path,'output',f"{user_id}_model_outputs.json")
        forecasted_expense= None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                forecasted_expense=float(data["forecasting"]["next_month_expense"].strip("$"))
                print("forceasted expenses:",forecasted_expense)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error: File not found - {file_path}")

        # Budget 
        budget=total_income+total_savings_amount-forecasted_expense
        budget_used_percent = (total_spendings / budget) * 100

        st.subheader("Monthly Income and Spendings")

        #Read income and expense data
        income_data = self.get_data1('income', columns=['date', 'amount'], user_id=user_id)
        income_data['date'] = pd.to_datetime(income_data['date'], format='%m/%d/%Y')

        spendings_data = self.get_data1('transactions', columns=['date', 'amount'], user_id=user_id)
        spendings_data['date'] = pd.to_datetime(spendings_data['date'], format='%m/%d/%Y')


        # Applying week_of_month method within the class DbUtils
        income_data['week_num'] = income_data['date'].apply(lambda date: self.week_of_month(date))
        spendings_data['week_num'] = spendings_data['date'].apply(lambda date: self.week_of_month(date))
        print("spendings_data",spendings_data)


        #Plot the line chart using pandas and Streamlit
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(income_data["week_num"], income_data["amount"], label="Income", color="blue")
        ax.plot(spendings_data["week_num"], spendings_data["amount"], label="Expenses", color="red")
        ax.set_xlabel("Week Number")
        ax.set_ylabel("Amount")
        ax.set_title("Income and Spending Over Time")
        plt.legend()
        st.pyplot(fig)

        #Financial Metrics With Card Visuals(Section 2)
        #---------------------------------------------#
        def KPI_metrics(title, value, text):
            st.markdown(f"""
                <div class = "metrics" style = "background-color: lightblue; padding: 10px 20px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
                    <h4>{title}</h4>
                    <p style = "font-size: 25px; margin: 0;">{value}</p>
                    <p style = "font-size: 15px; margin: 0; align: center;">{text}</p>
                </div>
                """, unsafe_allow_html = True)

        st.subheader("Financial Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            KPI_metrics("Spendings", f"${total_spendings}", "Amount spent so far this month")

        with col2:
            KPI_metrics("Net Income", f"${net_income}", "Total Net Income for this month")

        with col3:
            KPI_metrics("Budget", f"{budget_used_percent:.2f}%", "% of budget used this month")

        with col4:
            KPI_metrics("Net Worth", f"${net_worth}", "Total Net worth for this month")

        #Financial Goals with Pie Charts (Section 3)
        #------------------------------------------#
        data3 = pd.read_csv(os.path.join(self.data_path,'merge_goals.csv'))
        data3['by_when'] = pd.to_datetime(data3['by_when'])

        st.subheader('Financial Goals')
        if st.button("My Goals List"):
            st.write(data3)


        num_goals = len(data3)
        fig, axes = plt.subplots(1, num_goals, figsize = (5 * num_goals, 6))

        if num_goals == 1:
            axes = [axes]

        for idx, row in data3.iterrows():
            progress = row['amount_saved'] / row['amount_needed'] * 100
            ax = axes[idx]
            ax.set_aspect('equal')
            ax.pie([progress, 100 - progress], labels = ['Progress', 'Remaining'], autopct = '%1.1f%%', colors = ['lightblue', '#d3d3d3'])
            ax.set_title(row['goal_name'])
        st.pyplot(fig)



if __name__=='__main__':
    conv = Conversation('Hi my name Robert. Welcome to FinThrivin. How are you doing?')
    # conv.start_conversation()
    conv.financial_health_board('374576')
    # primary_details =['lakshmi', 'guddu', '01/15/1990']
    # print(conv.verify_user(primary_details))


                
                    




    
           
   
    