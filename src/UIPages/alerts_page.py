from pathlib import Path
import sys
import os
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header
import pandas as pd
from datetime import datetime

CURR_DIR = Path(__file__).resolve().parent
PARENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PARENT_DIR))
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class AlertsPage:

    def load_data(self):
        base_path = os.path.join(ROOT_DIR, 'data')
        file_paths = ['fixed_expenses.csv']

        data = {}
        for file_path in file_paths:
            df = pd.read_csv(f'{base_path}/{file_path}')
            data[file_path.split('.')[0]] = df
        return data

    def calculate_due_date(self, payment_due_date_str, today):
        if pd.isna(payment_due_date_str):
            return None
        
        try:
            day = int(payment_due_date_str)
            due_date = today.replace(day=day)
            if due_date < today:
                month = today.month % 12 + 1
                year = today.year if month > 1 else today.year + 1
                due_date = due_date.replace(month=month, year=year)
            return due_date
        except ValueError:
            return datetime.strptime(payment_due_date_str, '%Y-%m-%d').date()

    def calculate_due_dates(self, data, user_id):
        today = datetime.today().date()
        metrics = {}

        user_expenses = data['fixed_expenses'][data['fixed_expenses']['user_id'] == user_id]

        for _, row in user_expenses.iterrows():
            expense_type = row['expense_type']
            date_obj = datetime.strptime(row['payment_due_date'], "%m/%d/%Y").date()
            
            if date_obj.month == today.month and date_obj.year == today.year:
                due_date = date_obj
                days_until_due = (due_date - today).days

                if 0 <= days_until_due <= 5:
                    metrics[f'days_until_{expense_type}_due'] = days_until_due

        return metrics

    def render_alerts_page(self, user_id):
        data = self.load_data()
        metrics = self.calculate_due_dates(data, user_id)
        
        st.title("Alerts & Action Items")
        
        colored_header(label='Things to take action on!', description='', color_name='blue-30')

        user_expenses = data['fixed_expenses'][data['fixed_expenses']['user_id'] == user_id]
        displayed_expenses = set()

        for _, row in user_expenses.iterrows():
            expense_type = row['expense_type']
            if expense_type not in displayed_expenses:
                days_until_due = metrics.get(f'days_until_{expense_type}_due', 'Unknown')
                if days_until_due != 'Unknown':
                    st.write(f"- Your {expense_type} bill is due in {days_until_due} days. Consider taking action now.")
                    displayed_expenses.add(expense_type)

        add_vertical_space(2)
        colored_header(label='Things to look out for!', description='', color_name='red-30')
        add_vertical_space(2)
        colored_header(label='Yay! You are on the right path.', description='', color_name='green-30')

if __name__ == '__main__':
    AlertsPage().render_alerts_page(374576)