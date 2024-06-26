import streamlit as st
from PIL import Image
import sys
import os
from pathlib import Path
CURR_DIR = Path(__file__).resolve().parent
sys.path.insert(0,str(CURR_DIR))
from debt_strategy_plots import draw_plot
PARENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PARENT_DIR))
from db_utils import DbUtils
from models.expense_module import TransactionCategorize
from models.distribution.distribution_model import Distribution
from models.distribution.forcasting import ForecastSeries
from finance_planner_crew.main import run_agent
from models.debt_payment_output_user import DebtPaymentSimulator
import pandas as pd


class Insights(DbUtils):

    def __init__(self):
        super().__init__()
    
    def load_insights(self):
        #Title Page for Insights UI
        

        if 'button_clicked' not in st.session_state:
            st.session_state.button_clicked = None

        def show_info(button_name):
            st.session_state.button_clicked = button_name

        st.header("Insights Dashboard:bulb:", divider="rainbow")
        st.write('Insights customized for you, by you!')
        #Side Bar UI
        # user_input_container = st.sidebar.container()
        # image_path = os.path.join(CURR_DIR,'robert.jpeg')
        # with user_input_container:
        #     st.title('Welcome to Your Insights Chatbot')
        #     # "# Hello Smith!"
        #     # image = Image.open(r'C:\Users\Antony\Downloads\FinThrivinIcon.png')
        #     image = Image.open(image_path)
        #     st.image(image, caption="Hello, this is Smith, How can I help you today?")
        #     st.sidebar.chat_input("Ask FinThrivin Anything")
        
        if "total_savings" not in st.session_state:
            st.session_state.total_savings = None

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button(label="Clever ways to reduce your spending. Click here for more."):
                show_info('Clever ways to reduce your spending. Click here for more.')
            
        with col2:
            if st.button(label="Next month's forecasted income and spending. Click here for more."):
                show_info("Next month's forecasted income and spending. Click here for more.")
        with col3:
            if st.button(label="Pay and save wisely for the right things first. Click here for more."):
                show_info("Pay and save wisely for the right things first. Click here for more.")
        with col4:
            if st.button(label=f"Debt reduction ideas to help you save {st.session_state.total_savings }. Click here for more."):
                show_info(f"Debt reduction ideas to help you save {st.session_state.total_savings }. Click here for more.")
        
        if st.session_state.button_clicked == 'Clever ways to reduce your spending. Click here for more.':
            if st.session_state.user_id != None:
                # st.write(TransactionCategorize().get_top_expenses(int(st.session_state.user_id)))
                TransactionCategorize().get_top_expenses(int(st.session_state.user_id))
                recomendations = run_agent('expense_recommendation',str(st.session_state.user_id))
                st.write(recomendations)
                
        
        elif st.session_state.button_clicked == "Next month's forecasted income and spending. Click here for more.":
            if st.session_state.user_id != None:
                next_month_income,next_month_expense = ForecastSeries().run(int(st.session_state.user_id))
                # st.write(f"Your monthly predicted income : ${str(round(next_month_income,2))} \n\n monthly predicted expense : ${str(round(next_month_expense,2))}")
                st.write("By predicting future income and spending you are able to create realistic plans and budgets.")
                st.subheader("Here is your next month's forecasted income and spending.")
                col4, col5 = st.columns(2)
                col4.metric(label="Next Month's Predicted Income", value=f'${str(round(next_month_income,2))}')
                col5.metric(label="Next Month's Predicted Expense", value=f'${str(round(next_month_expense,2))}')

        elif st.session_state.button_clicked == "Pay and save wisely for the right things first. Click here for more.":
            if st.session_state.user_id != None:
                distribution = Distribution().run_distribution(int(st.session_state.user_id))
                # st.write(f"Your bucket distribution  -> \n\n{distribution}")
                total_budget = distribution["total_budget"]
                emergency_fund = distribution["emergency_fund"]
                short_term_goals = distribution["short_term_goal"]
                debt_repayment = distribution["debt_payment"]
                long_term_goals = distribution["long_term_goals"]
                st.markdown(f'You have saved a total of **${total_budget}.** We got this figure by taking your disposable income'
                         f' and adding the savings that you want to use to fulfill each of the categories.')
                st.write("Here is how you can allocate it to either pay for your debt, save for your goals or emergency fund.")

                st.markdown(f" i.) **$ {emergency_fund} for your Emergency Fund**: You can use this fund for unexpected expenses."
                        f" If you lose your income, you can use this fund to supplement your income.")
                st.markdown(f" ii.)  **${short_term_goals} for your Short-Term Goals:** In order to be in good financial health,"
                            f" it is beneficial to save for large expenses. You can use this fund to save up for expenses"
                            f" that are coming up in the short-term such as paying for a medical bill or replacing the"
                            f" tyres of your car.")
                st.markdown(f" iii.) **${debt_repayment} for your debt repayment:** If you pay your debt faster you can save "
                        f"alot of money on interest and you can use that money for other expenses. You can use this fund to "
                        f"accelarate paying off your debt. This should be extra debt payments with the assumption that you are paying"
                        f"the minimum amount due from your income.")
                st.markdown(f" iv.) **{long_term_goals} for your Long Term Goals:** You are more likely to achieve your long time "
                            f"plans if you start saving money today! You can use this fund for large expenses that you want to make in "
                        f"the long-term such as buying a house or going on a vacation.")

                st.write("Consider opening separate bank accounts for emergency fund, short term goals and long term goals."
                        "This makes it easier to track and reach your goals. Keep making smart choices and keep moving forward!")

        elif st.session_state.button_clicked == f'Debt reduction ideas to help you save {st.session_state.total_savings }. Click here for more.':
            if st.session_state.user_id != None:
                plans, st.session_state.total_savings =DebtPaymentSimulator.main(st.session_state.user_id)
                st.write("Paying your debt faster helps you save alot of money on interest in the long run. Here are ways "
                     "you can accelerate paying off your loans. This assumes that you have already paid the "
                     "monthly minimum amount required from your income.")
                # st.write(f"<h5 style='font-size:18px;'>your debt payment strategies: \n\nTotal savings - {total_savings} \n\nDebt Payment Strategy plans :</h5>",unsafe_allow_html=True)
                draw_plot(plans)
                # st.write(plans)
                df = pd.json_normalize(plans).set_index("Month")
                st.write(df)
                recomendations = run_agent('debt_negotiation',str(st.session_state.user_id))
                st.write(f"<h5 style='font-size:18px;'>your debt negotiation recommendations \n\n{recomendations}</h5>",unsafe_allow_html=True)

    
        

if __name__=='__main__':
    insights = Insights()
    insights.load_insights() 