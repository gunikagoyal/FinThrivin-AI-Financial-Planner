import json
from datetime import datetime, timedelta

def should_trigger_model(user_id, existing_data, current_data):
    if user_id not in existing_data.values():
        return True

    existing_distribution = existing_data.get('distribution', {})
    existing_forecasting = existing_data.get("forcasting", {})
    current_date = datetime.now()

    # Check for significant data changes from the model input values #-----> the below if condition needs to be changed. Bothe the dict objects doesn't have the same keys
    if current_data['next_month_income'] != existing_forecasting.get('next_month_income', 0) or \
       current_data['next_month_expense'] != existing_forecasting.get('next_month_expense', 0) or \
       current_data['total_savings'] != existing_distribution.get('total_savings', 0) or \
       current_data['total_debt'] != existing_distribution.get('total_debt', 0) or \
       current_data['amount_needed'] != existing_distribution.get('amount_needed', 0) or \
       current_data['rough_amount'] != existing_distribution.get('rough_amount', 0):
        return True

    # Check for weight or prioritization changes
    if current_data['weights'] != existing_distribution.get('weights', {}) or \
       current_data['prioritized_buckets'] != existing_distribution.get('prioritized_buckets', []):
        return True

    # Check for time threshold based on the first day of a new month
    last_update_str = existing_distribution.get('last_updated', '2024-01-01 00:00:00')
    last_update = datetime.strptime(last_update_str, '%m-%d-%Y %H:%M:%S')
    if current_date.year > last_update.year or \
       (current_date.year == last_update.year and current_date.month > last_update.month):
        # Check if today is the first day of the month
        if current_date.day == 1:
            return True

    return False