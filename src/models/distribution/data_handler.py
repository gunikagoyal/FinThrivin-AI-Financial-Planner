import pandas as pd
from pathlib import Path
import json

def load_and_merge_data(data_dir=Path('data')):
    users = pd.read_csv(data_dir / 'user.csv')
    debts = pd.read_csv(data_dir / 'debts.csv')
    long_terms = pd.read_csv(data_dir / 'long_term_goals.csv')
    short_term_goals = pd.read_csv(data_dir / 'short_term_goals.csv')
    savings = pd.read_csv(data_dir / 'savings.csv')
    forecast = pd.read_csv(data_dir / 'output_forecast.csv')
    print("Forecast Columns:", forecast.columns)
    users = users[['user_id', 'first_name', 'last_name']]
    debts = debts[['user_id', 'Loan Balance', 'Minimum_monthly_payment', 'Interest Rate']]
    long_terms = long_terms[['user_id', 'amount_needed', 'by_when']]
    short_term_goals = short_term_goals[['user_id', 'rough_amount', 'due_date']]
    savings = savings[['user_id', 'savings_amount']]
    #forecast = forecast[['user_id', 'next_month_income', 'next_month_expense']] this was for reading values from csv
    output_dir = data_dir / 'output'
    # Load forecast data from JSON files
    forecast_data = []
    for file in output_dir.glob('*.json'):
        with open(file, 'r') as f:
            data = json.load(f)
            user_id = data.get('user_id')
            forecasting = data.get('forecasting', {})
            next_month_income = forecasting.get('next_month_income', 0)
            next_month_expense = forecasting.get('next_month_expense', 0)
            forecast_data.append({
                'user_id': user_id,
                'next_month_income': next_month_income,
                'next_month_expense': next_month_expense
            })
    forecast = pd.DataFrame(forecast_data)
     # Convert monetary values from strings to floats
    forecast['next_month_income'] = forecast['next_month_income'].replace('[\$,]', '', regex=True).astype(float)
    forecast['next_month_expense'] = forecast['next_month_expense'].replace('[\$,]', '', regex=True).astype(float)
    
    debts_agg = debts.groupby('user_id').agg({
        'Loan Balance': 'sum',
        'Minimum_monthly_payment': 'sum',
        'Interest Rate': 'mean'
    }).reset_index()

    long_terms_agg = long_terms.groupby('user_id').agg({
        'amount_needed': 'sum',
        'by_when': 'max'
    }).reset_index()

    short_term_goals_agg = short_term_goals.groupby('user_id').agg({
        'rough_amount': 'sum',
        'due_date': 'max'
    }).reset_index()

    savings_agg = savings.groupby('user_id').agg({
        'savings_amount': 'sum'
    }).reset_index()

    forecast_agg = forecast.groupby('user_id').agg({
        'next_month_income': 'sum',
        'next_month_expense': 'sum'
    }).reset_index()

    merged_data = pd.merge(users, forecast_agg, on='user_id', how='left')
    merged_data = pd.merge(merged_data, debts_agg, on='user_id', how='left')
    merged_data = pd.merge(merged_data, long_terms_agg, on='user_id', how='left')
    merged_data = pd.merge(merged_data, short_term_goals_agg, on='user_id', how='left')
    merged_data = pd.merge(merged_data, savings_agg, on='user_id', how='left')

    merged_data.fillna(0, inplace=True)
    merged_data.to_csv(data_dir / 'input_distribution.csv', index=False)

    return merged_data

def prepare_user_data(user_id, merged_data, user_inputs):
    user_data = merged_data[merged_data['user_id'] == user_id]
    if user_data.empty:
        raise ValueError(f"No data found for user_id: {user_id}")
    user_data = user_data.iloc[0].to_dict()

    next_month_income = user_data['next_month_income']
    next_month_expense = user_data['next_month_expense']
    total_budget = next_month_income + user_data['savings_amount'] - next_month_expense

    user_input_data = user_inputs[user_inputs['user_id'] == user_id].iloc[0].to_dict()
   
    user_data_dict = {
        'user_id': user_data['user_id'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'next_month_income': next_month_income,
        'next_month_expense': next_month_expense,
        'total_budget': total_budget,
        'total_savings': user_data['savings_amount'],
        'total_debt': user_data['Loan Balance'],
        'short_term_goals': [
            {'amount': user_data['rough_amount'], 'due_date': user_data['due_date']}
        ],
        'long_term_goals_target': user_data['amount_needed'],
        'long_term_goals_by_when': user_data['by_when'],
        'bounds': {
            'expense_min': user_input_data['expense_min'],
            'expense_max': user_input_data['expense_max'],
            'emergency_fund_min': user_input_data['emergency_fund_min'],
            'emergency_fund_max': user_input_data['emergency_fund_max'],
            'debt_payment_min': user_input_data['debt_payment_min'],
            'debt_payment_max': user_input_data['debt_payment_max'],
            'long_term_goals_min': user_input_data['long_term_goals_min'],
            'long_term_goals_max': user_input_data['long_term_goals_max'],
        },
        'prioritized_buckets': user_input_data['prioritized_buckets'].split(','),
        'weights': {
            'Expense': user_input_data['expense_weight'] / 100,
            'Emergency Fund': user_input_data['emergency_fund_weight'] / 100,
            'Short-Term Goals': user_input_data['short_term_goals_weight'] / 100,
            'Debt Payment': user_input_data['debt_payment_weight'] / 100,
            'Long-Term Goals': user_input_data['long_term_goals_weight'] / 100
        }
    }

    return user_data_dict
