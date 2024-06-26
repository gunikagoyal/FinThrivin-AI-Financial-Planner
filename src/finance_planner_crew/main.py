from pathlib import Path
import json
import  pandas as pd
import sys
import os
from datetime import datetime
CURR_DIR = Path(__file__).resolve().parent
sys.path.insert(0,str(CURR_DIR))
from fetch_UserProfile import fetch_userProfile
from crew import FinancePlannerCrew
from condition_checks import Conditions
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def tip_section():
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

def run_agent(agent_selection, user_id=None,user_input=None):
    # finance_planner = FinancePlannerCrew()
    
    result = ''
    if agent_selection == 'education':
        inputs = {
        'tip_section' : None,
        'top_spendings': None,
        'json_Strategies': None,
        'user_prof_recon_debt': None,
        "topic": user_input
    }
        finance_planner = FinancePlannerCrew()
        finance_planner.set_single_agent(finance_planner.Resercher_agent())
        finance_planner.set_single_task(finance_planner.research_task())
        finance_planner.set_single_agent(finance_planner.recommendation_agent())
        finance_planner.set_single_task(finance_planner.Suggetion_task())
        result=finance_planner.crew().kickoff(inputs=inputs)
        return result
    
    output_path = os.path.join(ROOT_DIR,'data','output',f'{user_id}_model_outputs.json')
    with open(output_path, 'r') as file:
        data = json.load(file)
    top_spendings = data['top_spending_categories']['top_spendings']
    strategies_path = os.path.join(ROOT_DIR,'data','debt_negotiation_strategies.json')
    with open(strategies_path, 'r') as file:
        strategies = json.load(file)
    # strategies = load_json_data(output_path2)["Strategies"]
    # path to the user's financial profile
    profile_path = os.path.join(ROOT_DIR, 'data', f'{user_id}_financialProfile.json')

    # Checking if user's financial profile exists, if not fetch and create one
    if not os.path.exists(profile_path):
        fetch_userProfile(user_id)

    # Loading user's financial profile
    try:
        with open(profile_path, 'r') as file:
            user_profile_data = json.load(file)
    except FileNotFoundError:
        print("There was an error loading the user's financial profile.")
        return

    
    inputs = {
        'tip_section' : tip_section(),
        'top_spendings': top_spendings,
        'json_Strategies': strategies,
        'user_prof_recon_debt': user_profile_data,
        "topic": user_input
    }
    

    if agent_selection == 'expense_recommendation':
        result = data['top_spending_categories']['recommendations']
        if Conditions().is_data_changed(data['top_spending_categories']['last_updated'], user_id):
            finance_planner = FinancePlannerCrew()
            finance_planner.set_single_agent(finance_planner.spending_reduction_rececommendation_expert_agent())
            finance_planner.set_single_task(finance_planner.generate_spending_reduction_recommendation_task())
            result = finance_planner.crew().kickoff(inputs=inputs)
            current_datetime = datetime.now()
            data['top_spending_categories']['recommendations'] = result
            data['top_spending_categories']['last_updated'] = current_datetime.strftime("%m-%d-%Y %H:%M:%S")
            with open(output_path, 'w') as file:
                json.dump(data, file, indent=4)
        return result

    elif agent_selection == 'debt_negotiation':
        result = data['debt_negotiation']['recommendations']
        if Conditions().is_debt_recom_data_changed(data['debt_negotiation']['last_updated'], user_id):
            finance_planner = FinancePlannerCrew()
            finance_planner.set_single_agent(finance_planner.debt_negotiation_advisor_agent())
            finance_planner.set_single_task(finance_planner.generate_debt_negotiation_recommendation_task())
            result = finance_planner.crew().kickoff(inputs=inputs)
            data['debt_negotiation']['recommendations'] = result
            current_datetime = datetime.now()
            data['debt_negotiation']['last_updated'] = current_datetime.strftime("%m-%d-%Y %H:%M:%S")
            with open(output_path, 'w') as file:
                json.dump(data, file, indent=4)
        return result
    


if __name__ == "__main__":
    print("## Welcome to Finance Planner Crew")
    print('-------------------------------')

    user_id = '374576'
    agent_selection = 'debt_negotiation'

    if agent_selection not in ['expense_recommendation', 'debt_negotiation']:
        print("Invalid selection. Please choose either 'expense_recommendation' or 'debt_negotiation'.")
    else: 
        result = run_agent(agent_selection, user_id)
        print("\n\n########################")
        print("## Here is your personalized financial Plan Recommendation")
        print("########################\n")
        print(result)