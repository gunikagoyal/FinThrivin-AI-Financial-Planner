import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def draw_plot(data):
    payment_data = []
    extra_payment_data = []
    loan_balance_data = []

    for entry in data:
        month = entry["Month"]
        
        for key, value in entry["Payment Allocation"].items():
            payment_data.append({"Month": month, "Type": key, "Amount": float(value.replace('$', '').replace(',', ''))})
            
        for key, value in entry["Loan Balances"].items():
            loan_balance_data.append({"Month": month, "Type": key, "Amount": float(value.replace('$', '').replace(',', ''))})

    df_payment = pd.DataFrame(payment_data)
    df_loan_balance = pd.DataFrame(loan_balance_data)

    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(20, 5))  # Change to 1 row, 3 columns

    # Loop through axes and plot data
    plot_titles = ['Payment Allocation Over Time', 'Loan Balances Over Time']

    for i, (df, ax) in enumerate(zip([df_payment, df_loan_balance], axes)):
        for key, grp in df.groupby('Type'):
            ax.plot(grp['Month'], grp['Amount'], label=key)
        ax.set_title(plot_titles[i])
        ax.set_ylabel('Amount ($)')
        ax.set_xlabel('Month')
        ax.legend()
    

    
    # plt.show()
    st.pyplot(fig)
