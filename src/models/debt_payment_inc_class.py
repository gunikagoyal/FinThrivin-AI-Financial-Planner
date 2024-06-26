import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

class DebtPaymentSimulator:
    def __init__(self, debt_data, excess_funds):
        self.debt_data = debt_data
        self.excess_funds = excess_funds

    def simulate_monthly_payments_avalanche(self):
        debt_data = self.debt_data.copy()
        month_counter = 0
        all_payments_and_balances = []
        total_excess_funds = self.excess_funds

        print("Initial Debt Data:")
        print(debt_data)  # Debugging statement

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

                payment_allocation_with_names[key_payment] = payment_allocation[i]
                extra_payments_with_names[key_extra] = extra_payments[i]
                loan_balances_with_names[key_balance] = debt_data.at[i, 'Loan Balance']

            all_payments_and_balances.append({
                'Month': month_counter,
                'Payment Allocation': payment_allocation_with_names,
                'Extra Payments': extra_payments_with_names,
                'Loan Balances': loan_balances_with_names
            })

            # Print the results for the current month
            print(f"Month {month_counter}:")
            print("Extra Payments:")
            print(extra_payments_with_names)
            print("Loan Balances:")
            print(loan_balances_with_names)

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
            total_payment += sum(float(value) for value in month_data['Payment Allocation'].values())
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
            "Total Payment with Minimum EMIs": total_payment_with_minimums,
            "Total Payment with Optimized Plan": total_payment_optimized,
            "Total Savings": total_savings
        }

    @staticmethod
    def save_payment_plan_to_json(user_id, payment_plan, savings, output_json_path):
        # Get the current timestamp
        current_timestamp = datetime.now().isoformat()

        data_to_save = {
            'User ID': user_id,
            'Timestamp': current_timestamp,
            'Total Savings': savings['Total Savings'],
            'Payment Plan': payment_plan
        }
        with open(output_json_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
            
    @staticmethod
    def load_existing_data(output_json_path):
        if os.path.exists(output_json_path):
            with open(output_json_path, 'r') as f:
                return json.load(f)
        return None

    @staticmethod
    def main():
        user_id = int(input("Please enter the user ID: "))

        script_dir = os.path.abspath(os.path.dirname(__file__))
        parent_dir = os.path.dirname(script_dir)
        grandparent1_dir = os.path.dirname(parent_dir)
        grandparent2_dir = os.path.dirname(grandparent1_dir)

        debts_csv_path = os.path.join(grandparent2_dir, 'data', 'debts.csv')
        buckets_csv_path = os.path.join(grandparent2_dir, 'data', 'buckets.csv')
        output_json_path = os.path.join(grandparent2_dir, 'data', 'output_debt_payment.json')

        debt_data = pd.read_csv(debts_csv_path)
        excess_funds = pd.read_csv(buckets_csv_path)

        debt_data = debt_data[debt_data['user_id'] == user_id]
        excess_funds = excess_funds[excess_funds['user_id'] == user_id]

        if excess_funds.empty:
            print("No excess funds data found for the specified user ID.")
            return

        total_excess_funds = excess_funds['extra_debt_payment_bucket'].iloc[0]
        simulator = DebtPaymentSimulator(debt_data, total_excess_funds)

        existing_data = simulator.load_existing_data(output_json_path)

        if existing_data and existing_data['User ID'] == user_id:
            last_timestamp = datetime.fromisoformat(existing_data['Timestamp'])
            current_timestamp = datetime.fromisoformat(debt_data['Timestamp'].iloc[0])

            if last_timestamp >= current_timestamp:
                print("No changes detected since the last update. Exiting.")
                return

        full_payment_plan = simulator.simulate_full_payment_plan()

        savings = simulator.calculate_savings()
        print(f"Total Payment with Minimum EMIs: ${savings['Total Payment with Minimum EMIs']:.2f}")
        print(f"Total Payment with Optimized Plan: ${savings['Total Payment with Optimized Plan']:.2f}")
        print(f"Total Savings: ${savings['Total Savings']:.2f}")

        simulator.save_payment_plan_to_json(user_id, full_payment_plan, savings, output_json_path)
        print(f"Output saved to {output_json_path}")

if __name__ == "__main__":
    DebtPaymentSimulator.main()
