import pandas as pd
from pathlib import Path
from common_utils import CommonUtils
import random
import os
import numpy as np


ROOT_DIR = Path(__file__).resolve().parent.parent
class DbUtils:

    def __init__(self):
        self.data_path = os.path.join(ROOT_DIR,"data")
    
    def get_data(self, table1, table2, columns,user_id):
        df1 = pd.read_csv(os.path.join(self.data_path,f"{table1}.csv"))
        df2 = pd.read_csv(os.path.join(self.data_path,f"{table2}.csv"))
        df2 = df2[df2['user_id'].astype(str).str.contains(user_id)]
        df1 = df1[df1['user_id'].astype(str).str.contains(user_id)]
        combined_data = pd.merge(df1,df2,on='user_id',how="left")

        columns_drop = [col for col in combined_data.columns if col not in columns]
        combined_data = combined_data.drop(columns=columns_drop, axis=1)

        # combined_data = combined_data[combined_data['user_id'].astype(str).str.contains(user_id)]
        
        return combined_data
    
    def verify_user(self, primary_details):
        df = pd.read_csv(os.path.join(self.data_path,"user.csv"))
        
        user_record = df[(df['first_name'].str.lower()==primary_details[0].lower()) & 
                         (df['last_name'].str.lower()==primary_details[1].lower()) &
                         (df['date_of_birth']==CommonUtils().convert_date(primary_details[2]))]
        
        if not user_record.empty:
            # existing user
            user_id = user_record['user_id'].values[0]
            return "no",user_id
        else:
            #new user
            return "yes", None


    
    def add_new_user(self, primary_details):
        df = pd.read_csv(os.path.join(self.data_path,"user.csv"))
        dob_formatted = CommonUtils().convert_date(primary_details[2])
        new_user_id = self.generate_user_id(df)
        new_record = {
                'user_id':new_user_id,
                'first_name': primary_details[0],
                'last_name': primary_details[1],
                'date_of_birth': dob_formatted
            }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_csv(os.path.join(self.data_path, "user.csv"), index=False)
        return new_user_id

    def generate_user_id(self,df):

        existing_user_ids = set(df['user_id'])
        while True:
            # Generate a 6 digit random user_id
            random_user_id = random.randint(100000, 999999)

            if random_user_id not in existing_user_ids:
                return random_user_id
            
    def update_record(self,table_name,column, value, user_id):
        df = pd.read_csv(os.path.join(self.data_path,f"{table_name}.csv"))
        df.loc[df['user_id'] == int(user_id), column] = value
        print(df.loc[df['user_id'] == int(user_id), column].head() )
        df.to_csv(os.path.join(self.data_path, f"{table_name}.csv"), index=False)
        print(os.path.join(self.data_path, f"{table_name}.csv"))
    
    def create_profile(self,primary_details):
        user_id=self.add_new_user(primary_details)
        tables = ['buckets','debts','fixed_expenses','long_term_goals','savings','short_term_goals','variable_expenses']
        new_record = {
                'user_id':user_id,
        }
        for table in tables:
            df = df = pd.read_csv(os.path.join(self.data_path,f"{table}.csv"))
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            df.to_csv(os.path.join(self.data_path, f"{table}.csv"), index=False)
        return user_id
    # Function to add records to any tabels in our data
    def add_record_to_table(self, table_name, record):
        df_path = os.path.join(self.data_path, f"{table_name}.csv")
        df = pd.read_csv(df_path)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_csv(df_path, index=False)
        return 
    def add_income(self, user_id, fixed_income_monthly,extra_income_monthly):
        record = {
            'user_id': user_id,
            'fixed_income_monthly': fixed_income_monthly,
            'extra_income_monthly': extra_income_monthly,
        }
        return self.add_record_to_table('user', record)
    def add_long_term_goal(self, user_id, goal_name, amount_needed, by_when):
        record = {
            'user_id': user_id,
            'goal_name': goal_name,
            'amount_needed': amount_needed,
            'by_when': by_when
        }
        return self.add_record_to_table('long_term_goals', record)
    def add_short_term_goal(self, user_id, expense_name, rough_amount, target_date):
        record = {
            'user_id': user_id,
            'expense_name': expense_name,
            'rough_amount': rough_amount,
            'target_date': target_date
        }
        return self.add_record('short_term_goals', record)
    def add_savings(self, user_id, institution, account_type, savings_amount):
        record = {
            'user_id': user_id,
            'institution': institution,
            'account_type': account_type,
            'savings_amount': savings_amount
        }
        return self.add_record('savings', record)
    def add_variable_expense(self, user_id, merchant_info,transaction_description,amount):
    
        record = {
            'user_id': user_id,
            'merchant_info': merchant_info,
            'transaction_description': transaction_description,
            'amount': amount
        }
        return self.add_record('variable_expenses', record)

    def add_fixed_expense(self, user_id, expense_type, payment_due_date, amount):

        record = {
            'user_id': user_id,
            'expense_type': expense_type,
            'payment_due_date':payment_due_date,
            'amount': amount
        }
        return self.add_record('fixed_expenses', record)
    def add_debt(self, user_id, Debt_ID, debt_type, Loan_Balance, Minimum_monthly_payment, Interest_Rate, Loan_Tenure, institution):
        record = {
            'user_id': user_id,
            'Debt ID': Debt_ID,
            'debt_type': debt_type,
            'Loan Balance': Loan_Balance,
            'Minimum_monthly_payment': Minimum_monthly_payment,
            'Interest Rate': Interest_Rate,
            'Loan Tenure': Loan_Tenure,
            'institution': institution
        }
        return self.add_record('debts', record)
    def get_data1(self, table1, columns, user_id, table2=None):
        df1 = pd.read_csv(os.path.join(self.data_path, f"{table1}.csv"))
        df1 = df1[df1['user_id'].astype(str).str.contains(user_id)]
        if table2:
            df2 = pd.read_csv(os.path.join(self.data_path, f"{table2}.csv"))
            df2 = df2[df2['user_id'].astype(str).str.contains(user_id)]
            combined_data = pd.merge(df1, df2, on='user_id', how="left")
        else:
            combined_data = df1

        columns_drop = [col for col in combined_data.columns if col not in columns]
        combined_data = combined_data.drop(columns=columns_drop, axis=1)
        # combined_data = combined_data[combined_data['user_id'].astype(str).str.contains(user_id)]

        return combined_data
    
    def rename_csv_columns(self, filename, old_col1, new_col1, old_col2, new_col2):
        # Read the CSV file into a DataFrame
        file_path = os.path.join(self.data_path, filename)
        df = pd.read_csv(file_path)

        # Rename the columns
        df = df.rename(columns={old_col1: new_col1, old_col2: new_col2})
        print(df.head())
        # Save the updated DataFrame back to the CSV file
        output_path = os.path.join(self.data_path, f"converted_{filename}")
        df.to_csv(output_path, index=False)

        return output_path
    
    def convert_due_date(self, filename, month, year, user_id):
        file_path = os.path.join(self.data_path, filename)
        df = pd.read_csv(file_path)
        df = df[df['user_id'].astype(str).str.contains(user_id)]

        # Convert 'payment_due_date' to mm/dd/yyyy format
        print(df.head())
        def convert_to_date(day):
            return f"{month}/{int(day):02d}/{year}"

        # df['payment_due_date'] = df['payment_due_date'].apply(convert_to_date)

         # Rename 'payment_due_date' column to 'date'
        df.rename(columns={'payment_due_date': 'date'}, inplace=True)
        df.rename(columns={'expense_type': 'transaction_description'}, inplace=True) # rename column
        
        # Save the updated DataFrame back to the CSV file
        output_path = os.path.join(self.data_path, f"converted_{filename}")
        df.to_csv(output_path, index=False)

        return output_path
    
    # Merges two CSV files and keeps only the specified columns.

    
    def merge_data(self,table1, table2, desired_columns):

        # Read CSV files
        df1 = pd.read_csv(os.path.join(self.data_path,f"{table1}.csv"))
        df2 = pd.read_csv(os.path.join(self.data_path,f"{table2}.csv"))

        # Combine data (assuming user_id is the common key)
        combined_data = pd.concat([df1[desired_columns], df2[desired_columns]], ignore_index=True)

        # Sort by date (optional)
        combined_data = combined_data.sort_values(by="date")

        # Save the combined data
        # combined_data.to_csv(merged_file, index=False)

        # print(f"Files merged successfully! Output saved to: {merged_file}")
        return (combined_data)
    
    # Function to compute week number of the month
    @staticmethod
    def week_of_month(dt):
        first_day = dt.replace(day=1)
        dom = dt.day
        adjusted_dom = dom + first_day.weekday()
        return int(np.ceil(adjusted_dom / 7.0))
    


if __name__=='__main__':
    db = DbUtils()
    columns_needed = ["user_id",	"transactional_Dates",	"Transactional_catogories",	"Amount",	"description",	"type_of_transactions","Monthly_Income",	"Annual_income"]
    # df = db.get_data('transactional_data','user',columns_needed,'user_id')
    # print(df.head())
    # user= db.verify_user('lakshmi','narayan','1983-05-13')
    # if user is None:
    #     new_user=db.add_new_user('lakshmi','narayan','1983-05-13')
    #     print(f"new user: {new_user}")
    # else:
    #     print(f'existing user: {user}')
    # db.update_record('user','410860','Occupation','software Engineer')
    primary_details =['optImum', 'aI', '01/01/2001']
    print(db.verify_user(primary_details))
