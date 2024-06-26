import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class DebtPaymentSimulator:
    def __init__(self, debt_data, excess_funds):
        self.debt_data = debt_data
        self.excess_funds = excess_funds

    def simulate_monthly_payments_avalanche(self):
        debt_data = self.debt_data.copy()
        month_counter = 0
        all_payments_and_balances = []
        total_excess_funds = self.excess_funds

        # print("Initial Debt Data:")
        # print(debt_data)  # Debugging statement

        while debt_data['Loan Balance'].sum() > 0:
            month_counter += 1

            # Allocate payments using the avalanche method
            debt_data = debt_data.sort_values(by='Interest Rate', ascending=False).reset_index(drop=True)

            # Make minimum payments first
            payment_allocation = debt_data['Minimum_monthly_payment'].copy()

            # Allocate excess funds to the highest interest rate debt
            remaining_excess_funds = total_excess_funds
            for i in range(len(debt_data)):
                if remaining_excess_funds > 0:
                    payment_allocation[i] += remaining_excess_funds
                    if payment_allocation[i] > debt_data.at[i, 'Loan Balance']:
                        remaining_excess_funds = payment_allocation[i] - debt_data.at[i, 'Loan Balance']
                        payment_allocation[i] = debt_data.at[i, 'Loan Balance']
                    else:
                        remaining_excess_funds = 0

            # Apply payments and update loan balances
            for i in range(len(debt_data)):
                debt_data.at[i, 'Loan Balance'] -= payment_allocation[i]

            # Calculate the remaining loan balances with interest for the next month
            for i in range(len(debt_data)):
                if debt_data.at[i, 'Loan Balance'] > 0:
                    debt_data.at[i, 'Loan Balance'] *= (1 + debt_data.at[i, 'Interest Rate'] / 12)

            # Calculate extra payments
            extra_payments = payment_allocation - debt_data['Minimum_monthly_payment']

            # Store the results
            payment_allocation_with_names = {}
            extra_payments_with_names = {}
            loan_balances_with_names = {}

            for i in range(len(debt_data)):
                debt_id = debt_data.at[i, 'Debt ID']
                loan_type = debt_data.at[i, 'Debt_type']
                key_payment = f"debt{debt_id}_{loan_type}_payment"
                key_extra = f"debt{debt_id}_{loan_type}_extra_payment"
                key_balance = f"debt{debt_id}_{loan_type}_balance"

                payment_allocation_with_names[key_payment] = f"${payment_allocation[i]:.2f}"
                extra_payments_with_names[key_extra] = f"${extra_payments[i]:.2f}"
                loan_balances_with_names[key_balance] = f"${debt_data.at[i, 'Loan Balance']:.2f}"


            all_payments_and_balances.append({
                'Month': month_counter,
                'Payment Allocation': payment_allocation_with_names,
                'Extra Payments': extra_payments_with_names,
                'Loan Balances': loan_balances_with_names
            })

            # Print the results for the current month
            # print(f"Month {month_counter}:")
            # print("Extra Payments:")
            # print(extra_payments_with_names)
            # print("Loan Balances:")
            # print(loan_balances_with_names)

            # Add the minimum payment of paid-off debts to excess funds
            paid_off_debts = debt_data[debt_data['Loan Balance'] <= 0]
            total_excess_funds += paid_off_debts['Minimum_monthly_payment'].sum()

            # Remove debts that have been paid off
            debt_data = debt_data[debt_data['Loan Balance'] > 0].reset_index(drop=True)

        return all_payments_and_balances

    def simulate_full_payment_plan(self):
        return self.simulate_monthly_payments_avalanche()

    def calculate_total_payment_from_plan(self, payment_plan):
        total_payment = 0
        for month_data in payment_plan:
            total_payment += sum(float(value.strip('$')) for value in month_data['Payment Allocation'].values())
        return total_payment

    def calculate_savings(self):
        debt_data = self.debt_data.copy()

        # Extract monthly payments from debt_data
        monthly_payments = debt_data['Minimum_monthly_payment']

        # Calculate total payment with minimum EMIs
        total_payment_with_minimums = (monthly_payments * debt_data['Loan Tenure']).sum()

        # Calculate total payment with optimized plan
        full_payment_plan = self.simulate_full_payment_plan()
        total_payment_optimized = self.calculate_total_payment_from_plan(full_payment_plan)

        total_savings = total_payment_with_minimums - total_payment_optimized

        return {
            "Total Payment with Minimum EMIs": f"${total_payment_with_minimums:.2f}",
            "Total Payment with Optimized Plan": f"${total_payment_optimized:.2f}",
            "Total Savings": f"${total_savings:.2f}"
        }

    @staticmethod
    def save_payment_plan_to_json(user_id, payment_plan, savings, output_json_folder):
        # Load the existing JSON file for the user
        user_file_path = DebtPaymentSimulator.find_user_file(user_id, output_json_folder)
        if not user_file_path:
            print(f"No JSON file found for user ID {user_id}.")
            return

        with open(user_file_path, 'r') as f:
            user_data = json.load(f)

        # Update the debt_payment_strategy section
        timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        user_data['debt_payment_strategy'] = {
            'last_updated': timestamp,
            'Total Savings': savings['Total Savings'],
            'Payment Plan': payment_plan
        }

        # Save the updated JSON file
        with open(user_file_path, 'w') as f:
            json.dump(user_data, f, indent=4)

        # print(f"Output saved to {user_file_path}")

    @staticmethod
    def find_user_file(user_id, output_json_folder):
        # Search for the file using the user ID in the file name
        for filename in os.listdir(output_json_folder):
            if str(user_id) in filename:
                file_path = os.path.join(output_json_folder, filename)
                if os.path.isfile(file_path):
                    return file_path
        return None
            
    @staticmethod
    def load_existing_data(output_json_path):
        if os.path.exists(output_json_path):
            with open(output_json_path, 'r') as f:
                return json.load(f)
        return None

    @staticmethod
    def find_user_file(user_id, output_json_folder):
        for filename in os.listdir(output_json_folder):
            if str(user_id) in filename:
                file_path = os.path.join(output_json_folder, filename)
                if os.path.isfile(file_path):
                    return file_path
        return None
    
    @staticmethod
    def timestamps_up_to_date(debt_data_timestamp, json_data):
        current_time = datetime.now()
    
        debt_payment_strategy_updated = True
        distribution_updated = True

        # Convert debt data timestamp to datetime
        #debt_data_timestamp = datetime.strptime(debt_data_timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")

        # Check debt_payment_strategy timestamp
        if 'debt_payment_strategy' in json_data:
            last_updated_str = json_data['debt_payment_strategy'].get('last_updated', '')
            if last_updated_str:
                last_timestamp = datetime.strptime(last_updated_str, "%m-%d-%Y %H:%M:%S")
                if last_timestamp >= debt_data_timestamp:
                    debt_payment_strategy_updated = False

        # Check distribution timestamp
        distribution_last_updated_str = json_data['distribution'].get('last_updated', '')
        if distribution_last_updated_str:
            distribution_last_timestamp = datetime.strptime(distribution_last_updated_str, "%m-%d-%Y %H:%M:%S")
            if distribution_last_timestamp >= current_time:
                distribution_updated = False

        return debt_payment_strategy_updated or distribution_updated
    
    @staticmethod
    def main(user_id):
        # user_id = int(input("Please enter the user ID: "))
        user_id = int(user_id)
        # script_dir = os.path.abspath(os.path.dirname(__file__))
        # parent_dir = os.path.dirname(script_dir)
        # grandparent1_dir = os.path.dirname(parent_dir)
        # grandparent2_dir = os.path.dirname(grandparent1_dir)

        debts_csv_path = os.path.join(ROOT_DIR, 'data', 'debts.csv')
        output_json_folder = os.path.join(ROOT_DIR, 'data', 'output')
        # debts_csv_path = os.path.join(grandparent2_dir, 'data', 'debts.csv')
        # output_json_folder = os.path.join(grandparent2_dir, 'data', 'output')

        debt_data = pd.read_csv(debts_csv_path)

        debt_data = debt_data[debt_data['user_id'] == user_id]

        #Userprofile
        required_columns = ['Debt ID', 'Debt_type', 'Loan Balance', 'Interest Rate', 'Minimum_monthly_payment', 'Loan Tenure']
        if debt_data[required_columns].isnull().any().any():
            print("User profile info is not complete.")
            return

        user_file_path = DebtPaymentSimulator.find_user_file(user_id, output_json_folder)
        if not user_file_path:
            print(f"No JSON file found for user ID {user_id}.")
            return

        with open(user_file_path, 'r') as f:
            user_data = json.load(f)

        excess_funds = user_data['distribution']['debt_payment']
        
        update_needed = False

        if 'debt_payment_strategy' in user_data:
            last_updated_str = user_data['debt_payment_strategy'].get('last_updated', '')
            if last_updated_str:
                last_timestamp = datetime.strptime(last_updated_str, "%m-%d-%Y %H:%M:%S")
                current_timestamp = datetime.strptime(debt_data['Timestamp'].iloc[0], "%Y-%m-%dT%H:%M:%S.%f")
                # Extract the last updated timestamp from the distribution key in output.json
                distribution_last_updated_str = user_data['distribution'].get('last_updated', '')
                distribution_timestamp = datetime.strptime(distribution_last_updated_str, "%m-%d-%Y %H:%M:%S")

                # If either condition is not met, set update_needed to True
                if last_timestamp < current_timestamp or last_timestamp < distribution_timestamp:
                    update_needed = True
            else:
                update_needed = True
        else:
            update_needed = True

        if not update_needed:
            print("No changes detected since the last update. Exiting.")
            return user_data['debt_payment_strategy']['Payment Plan'], user_data['debt_payment_strategy']['Total Savings']
        else:
            simulator = DebtPaymentSimulator(debt_data, excess_funds)

            full_payment_plan = simulator.simulate_full_payment_plan()

            savings = simulator.calculate_savings()
            # print(f"Total Payment with Minimum EMIs: {savings['Total Payment with Minimum EMIs']}") 
            # print(f"Total Payment with Optimized Plan: {savings['Total Payment with Optimized Plan']}")
            # print(f"Total Savings: {savings['Total Savings']}")

            simulator.save_payment_plan_to_json(user_id, full_payment_plan, savings, output_json_folder)
            # print(f"Output saved to {output_json_folder}")
            return full_payment_plan,savings
        
if __name__ == "__main__":
    payment_plans, savings = DebtPaymentSimulator.main('374576')
    print(f' actual plans ==== {payment_plans}')
    print(f" actual savings ===={savings}")
