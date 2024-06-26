
"""
Expense Tracking: Categorize expenses automatically using autonlp from huggingface.co and 
track them against a budget, providing real-time insights into spending habits to help users make informed decisions.
"""

from langchain.tools import tool
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import pandas as pd
from pathlib import Path
import os
from crewai_tools import BaseTool
from typing import Any

# Load the pretrained model and tokenizer from Hugging Face
model_name = "mgrella/autonlp-bank-transaction-classification-5521155"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
categories = list(model.config.id2label.values())

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
data_path = os.path.join(ROOT_DIR,"data")
bank_transactions = pd.read_csv(os.path.join(data_path,"dataset_transaction.csv"))


class MyExpenseAnalyzerTool(BaseTool):
    name: str = "Categorize_expenses_identify_top_spending_areas"
    description: str = "This tool categorize expenses, identifiesand returns top 5 spending categories."    
    #def __init__(self):
    #    pass

    def _run(self, **kwargs: Any) -> str:
        try:

            def categorize_transaction(text):
                inputs = tokenizer(text, return_tensors="pt", truncation=True)
                outputs = model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1).squeeze().tolist()
                category_idx = probabilities.index(max(probabilities))
                full_category = categories[category_idx]
                # Function to extract reduced category from full category
                #reduced_category = lambda full_category : full_category.split('_')[0]
                reduced_category = full_category.split('_')[0]
                reduced_category = (re.search(r"Category\.(\w+)", reduced_category)).group(1)
                #print("reduced_category printed", reduced_category)
                return reduced_category


            # Categorize transactions
            bank_transactions['category'] = bank_transactions['Bank_Transaction'].apply(categorize_transaction)

            # Display the categorized transactions
            print(bank_transactions[['Bank_Transaction', 'category']])

            bank_transactions.to_csv("categorized_transactions.csv", index=False)

            # Remove the dollar symbol and convert 'Amount' column to float
            bank_transactions['Amount'] = bank_transactions['Amount'].astype(str)
            bank_transactions['Amount'] = bank_transactions['Amount'].apply(lambda x: re.sub(r'[$,]', '', x)).astype(float)

            # Group by category and sum the amounts
            category_amounts = bank_transactions.groupby('category')['Amount'].sum()
            # Print the category amounts
            print("categorized amounts:", category_amounts)

            # Top 5 spending amounts
            top_5_spending_areas = category_amounts.sort_values(ascending=False).head(5)

            # Print the top 5 category amounts
            print("top 5 spending areas", top_5_spending_areas)

            return top_5_spending_areas

        except Exception as e:
            return f"Error: An unexpected error occurred while categorizing expenses - {str(e)}"

