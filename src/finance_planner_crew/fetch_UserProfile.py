import pandas as pd
import json
import os

def fetch_userProfile(user_id):
    # Define the base path to the data directory
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    user_id = int(user_id)
    
    # 5 Files loading functions

    # Loading 4 csv's data
    debts_df = pd.read_csv(os.path.join(base_path, 'debts.csv'))
    user_df = pd.read_csv(os.path.join(base_path, 'user.csv'))
    goals_df = pd.read_csv(os.path.join(base_path, 'merge_goals.csv'))
    savings_df = pd.read_csv(os.path.join(base_path, 'savings.csv'))
    # Loading the customer's credit profile data
    credit_data_path = os.path.join(base_path, f"{user_id}_credit_management_synthetic_data.json")
    with open(credit_data_path, 'r') as f:
        credit_data = json.load(f)

    # Filter data by user_id
    user_info = user_df[user_df['user_id'] == user_id].copy()
    user_debts = debts_df[debts_df['user_id'] == user_id]
    user_goals = goals_df[goals_df['user_id'] == user_id]
    user_savings = savings_df[savings_df['user_id'] == user_id]

    # Calculate net income
    if not user_info.empty:
        user_info['net_income'] = user_info['fixed_income_monthly'] + user_info['extra_income_monthly']

    # Create user profile dictionary
    user_profile = {
        str(user_id): {
            "User Details": user_info.drop('user_id', axis=1).to_dict(orient='records'),
            "Debts": user_debts.drop('user_id', axis=1).to_dict(orient='records'),
            "Financial Goals": user_goals.drop('user_id', axis=1).to_dict(orient='records'),
            "Savings Accounts": user_savings.drop('user_id', axis=1).to_dict(orient='records'),
            "Credit Report": credit_data["credit_report"],
            "Financial Behaviors": credit_data["financial_behaviors"]
        }
    }

    # Output to JSON file
    output_path = os.path.join(base_path, f"{user_id}_financialProfile.json")
    with open(output_path, 'w') as f:
        json.dump(user_profile, f, indent=4)
    # print(f"Financial profile for user {user_id} saved as {output_path}")
    return output_path



# if __name__ == '__main__':
#     user_id = input("Enter the user_id to fetch financial information: ")
#     fetch_userProfile(user_id)
