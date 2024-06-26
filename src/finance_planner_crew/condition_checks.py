import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Conditions:

    def __init__(self):
        self.data_path=os.path.join(ROOT_DIR,'data')

    def is_data_changed(self,model_ran_date,user_id, timestamp_column='last_updated',):
        tables = ['fixed_expenses.csv','variable_expenses.csv']
        data_chaged = False
        for table in tables:
            file_path = os.path.join(self.data_path, table)
            df = pd.read_csv(file_path)
            df= df[df['user_id'].astype(str).str.contains(user_id)]
            # Convert the timestamp column to datetime objects
            df[timestamp_column] = pd.to_datetime(df[timestamp_column], format="%m-%d-%Y %H:%M:%S")

            # Calculate the threshold date
            # threshold_date = datetime.now() - timedelta(days=days_threshold)
            model_ran = datetime.strptime(model_ran_date, "%m-%d-%Y %H:%M:%S")

            # Debug output
            print(f"Threshold date: {model_ran}")

            # Check if any timestamp is within the threshold
            recent_updates = df[timestamp_column] > model_ran

            if recent_updates.any():
                    data_chaged = True

            # Debug output
            print(f"Timestamps within threshold: {df[recent_updates][timestamp_column]}")

        return data_chaged
    

    def is_debt_recom_data_changed(self, model_ran_date, user_id, timestamp_column='last_updated'): # model_ran_date is the last_updated date of the model from model_outputs.json
            tables = ["debts.csv", "user.csv", "savings.csv"]
            model_ran = datetime.strptime(model_ran_date, "%m-%d-%Y %H:%M:%S")  
            # print(f"Model ran date: {model_ran}") 
            change_count = False
            for table in tables:
                file_path = os.path.join(self.data_path, table)
                df = pd.read_csv(file_path)
                df= df[df['user_id'].astype(str).str.contains(str(user_id))]
                df[timestamp_column] = pd.to_datetime(df[timestamp_column], format="%m-%d-%Y %H:%M:%S")
                recent_updates = df[timestamp_column] > model_ran #  05-30-2024 18:53:21
                # print(recent_updates)
                if recent_updates.any():
                    change_count = True
            # print(change_count)
            return change_count # True if change_count >= 2 else False # checks if Data is updated in two or more tablese if change_count >= 2 else False # checks if Data is updated in two or more tables
            

if __name__ == '__main__':
    con = Conditions()
    user_id = '374576'
    file_path = os.path.join(con.data_path, "fixed_expenses.csv")
    output_path = os.path.join(con.data_path,'output',f'{user_id}_model_outputs.json')
    with open(output_path, 'r') as file:
            data = json.load(file)
    model_run_date = data['top_spending_categories']['last_updated']

    if con.is_data_changed(model_run_date,  user_id):
        print("model ran before data changed then call model")
    else:
         print("model ran after data changed-- no call")

    model_run_date_2 = data['debt_negotiation']['last_updated']

    if con.is_debt_recom_data_changed(model_run_date_2):
        print("Data has changed in two or more critical files, running the model again.")
    else:
        print("Data has not changed significantly; no need to rerun the model.")