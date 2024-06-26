import json
import pandas as pd
from prophet import Prophet
from datetime import datetime
from pathlib import Path
import os
import warnings
import logging

# Suppress specific warnings and set up logging
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
logger = logging.getLogger('cmdstanpy')
logger.setLevel(logging.ERROR)

for handler in logger.handlers:
    logger.removeHandler(handler)

logger.addHandler(logging.NullHandler())

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class ForecastSeries:
    def __init__(self):
        self.data_path = os.path.join(ROOT_DIR, 'data')

    def load_data(self, user_id):
        # Load necessary data
        user_df = pd.read_csv(os.path.join(self.data_path, 'user.csv'))
        var_expenses_df = pd.read_csv(os.path.join(self.data_path, 'variable_expenses.csv'))
        fixed_expenses_df = pd.read_csv(os.path.join(self.data_path, 'fixed_expenses.csv'))
        income_df = pd.read_csv(os.path.join(self.data_path, 'income.csv'))

        # Print the content of each DataFrame to inspect for NaN values
        print("User Data:")
        print(user_df.head())
        print("Variable Expenses Data:")
        print(var_expenses_df.head())
        print("Fixed Expenses Data:")
        print(fixed_expenses_df.head())
        print("Income Data:")
        print(income_df.head())

        # Filter data for the specific user_id
        user_data = user_df[user_df['user_id'] == user_id]
        var_expenses_df = var_expenses_df[var_expenses_df['user_id'] == user_id]
        fixed_expenses_df = fixed_expenses_df[fixed_expenses_df['user_id'] == user_id]
        income_df = income_df[income_df['user_id'] == user_id]

        return user_data, var_expenses_df, fixed_expenses_df, income_df

    def preprocess_data(self, user_data, var_expenses_df, fixed_expenses_df, income_df):
        # Add fixed income to income data
        fixed_income = user_data['fixed_income_monthly'].values[0]
        income_df['amount'] += fixed_income

        # Initialize expenses list
        income_df['months'] = income_df['date'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y').strftime('%Y-%m'))
        months = income_df['months']
        expenses = [fixed_expenses_df['amount'].sum()] * len(months)

        # Sum up variable expenses for each month
        for i, row in var_expenses_df.iterrows():
            date = row['date']
            month = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m')
            try:
                idx = months[months == month].index[0]
                expenses[idx] += row['amount']
            except IndexError:
                print(f"No matching entry found for month: {month} in income.csv")

        return months, income_df['amount'], expenses

    def prepare_dataframes(self, months, income, expenses):
        # Create combined dataframe
        data_df = pd.DataFrame({
            'Month': months,
            'Income': income,
            'Expenses': expenses
        })

        # Convert dates and drop NaNs
        data_df['Month'] = pd.to_datetime(data_df['Month'], format='%Y-%m')
        data_df.dropna(inplace=True)

        # Ensure no NaNs in the 'Income' and 'Expenses' columns
        data_df['Income'] = data_df['Income'].ffill()
        data_df['Expenses'] = data_df['Expenses'].ffill()

        # Ensure that there are more than one unique date
        if data_df['Month'].nunique() < 2:
            print(f"Data after date conversion and dropping NaNs:\n{data_df}")
            raise ValueError("Not enough data after preprocessing to fit the model.")

        # Prepare data for Prophet
        income_df = data_df[['Month', 'Income']].rename(columns={'Month': 'ds', 'Income': 'y'})
        expense_df = data_df[['Month', 'Expenses']].rename(columns={'Month': 'ds', 'Expenses': 'y'})

        income_df['ds'] = pd.to_datetime(income_df['ds'])
        expense_df['ds'] = pd.to_datetime(expense_df['ds'])

        return income_df, expense_df

    def forecast(self, df):
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=1)
        forecast = model.predict(future)
        return forecast['yhat'].iloc[-1]

    def update_output_json(self, user_id, next_month_income, next_month_expense):
        ct = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
        json_file = os.path.join(self.data_path, 'output', f'{user_id}_model_outputs.json')
        
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data['forecasting'] = {
            'last_updated': ct,
            'next_month_income': f"${next_month_income:.2f}",
            'next_month_expense': f"${next_month_expense:.2f}"
        }

        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)

    def run(self, user_id):
        user_data, var_expenses_df, fixed_expenses_df, income_df = self.load_data(user_id)
        months, income, expenses = self.preprocess_data(user_data, var_expenses_df, fixed_expenses_df, income_df)

        try:
            income_df, expense_df = self.prepare_dataframes(months, income, expenses)
            print("Prepared income data for Prophet:")
            print(income_df)
            print("Prepared expense data for Prophet:")
            print(expense_df)

            next_month_income = self.forecast(income_df)
            next_month_expense = self.forecast(expense_df)
            self.update_output_json(user_id, next_month_income, next_month_expense)
            print(f"Forecasting successful for user_id: {user_id}")
            return next_month_income,next_month_expense
        except Exception as e:
            print(f"Error during prediction: {e}")

if __name__ == "__main__":
    forecasting = ForecastSeries()
    forecasting.run(374576)
