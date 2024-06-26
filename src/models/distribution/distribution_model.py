from pathlib import Path
import sys
CURR_DIR = Path(__file__).resolve().parent
sys.path.insert(0,str(CURR_DIR))
import os
import pandas as pd
import json
from datetime import datetime
from data_handler import load_and_merge_data, prepare_user_data
from optimization import optimize_allocation_pulp
from trigger_model import should_trigger_model



ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
OUTPUT_DIR = DATA_DIR / 'output'

class Distribution:
    def __init__(self):
        self.data_dir= os.path.join(ROOT_DIR,'data')
        self.output_dir = os.path.join(OUTPUT_DIR,'output')



    def load_user_inputs(self,user_id, file_path=DATA_DIR / 'optimization_inputs.csv'):
        user_inputs = pd.read_csv(file_path)
        user_inputs=user_inputs[user_inputs['user_id'].astype(str).str.contains(str(user_id))]
        return user_inputs

    def load_existing_output(self,user_id):
        file_path = OUTPUT_DIR / f'{user_id}_model_outputs.json'
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def convert_to_serializable(self,data):
        if isinstance(data, dict):
            return {k: self.convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_to_serializable(i) for i in data]
        elif isinstance(data, pd.Timestamp):
            return data.strftime('%m-%d-%Y %H:%M:%S')
        elif isinstance(data, (pd.Int64Dtype, pd.UInt64Dtype, pd.Series, pd.Index, int)):
            return int(data)
        elif isinstance(data, (float, str)):
            return data
        else:
            return str(data)

    def update_output_data(self,user_id, new_data):
        file_path = OUTPUT_DIR / f'{user_id}_model_outputs.json'
        existing_data = self.load_existing_output(user_id)

        if "distribution" in existing_data:
            existing_data["distribution"] = new_data
        else:
            existing_data["distribution"] = new_data

        existing_data["user_id"] = user_id
        existing_data["created_date"] = existing_data.get("created_date", datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        existing_data["distribution"]["last_updated"] = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

        serializable_data = self.convert_to_serializable(existing_data)

        with open(file_path, 'w') as file:
            json.dump(serializable_data, file, indent=4)

    def run_distribution(self,user_id):
        user_inputs = self.load_user_inputs(user_id)
        merged_data = load_and_merge_data(DATA_DIR)
        print("Merged Data:")
        print(merged_data.head())

        # for user_id in user_inputs['user_id']:
        print(f"Processing user_id: {user_id}")
        user_data_dict = prepare_user_data(user_id, merged_data, user_inputs)
        # if user_data_dict is None:
        #     continue

        existing_output = self.load_existing_output(user_id)
        
        if should_trigger_model(user_id, existing_output, user_data_dict):
            try:
                allocation = optimize_allocation_pulp(user_data_dict)
                new_output = {
                    "last_updated": datetime.now().strftime('%m-%d-%Y %H:%M:%S'),
                    "total_budget": user_data_dict['total_budget'],
                    #"next_month_income": user_data_dict['next_month_income'],
                    #"next_month_expense": user_data_dict['next_month_expense'],
                    "expense": user_data_dict['next_month_expense'],
                    "emergency_fund": allocation['emergency_fund'],
                    "short_term_goal": allocation['short_term_goal'],
                    "debt_payment": allocation['debt_payment'],
                    "long_term_goals": allocation['long_term_goals'],
                    "prioritized_buckets": user_data_dict['prioritized_buckets'],
                    "weights": user_data_dict['weights']
                }
                self.update_output_data(user_id, new_output)
                print(f"Optimization successful for user_id: {user_id}")
            except Exception as e:
                print(f"Optimization failed for user_id: {user_id} with error: {e}")
            return new_output
        else:
            return existing_output

if __name__ == '__main__':
    user = 374576
    dis = Distribution()
    dis.run_distribution(user)
