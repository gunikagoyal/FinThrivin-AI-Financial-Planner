from datetime import datetime

class CommonUtils:
    def __init__(self):
        pass

    def convert_date(self,date_str):
        """
        Convert user-entered date to mm/dd/yyyy format as text.
        """
        formats = [
            '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y',
            '%Y-%m-%d', '%Y/%m/%d', '%m-%d-%Y', '%m-%d-%y',
            '%d-%m-%Y', '%d-%m-%y', '%m.%d.%Y', '%m.%d.%y',
            '%d.%m.%Y', '%d.%m.%y', '%Y.%m.%d', '%Y %m %d',
            '%m %d %Y', '%d %m %Y', '%Y %d %m', '%Y %m %d'
        ]
        
        for format_str in formats:
            try:
                parsed_date = datetime.strptime(date_str, format_str).date()
                return parsed_date.strftime('%m/%d/%Y')
            except ValueError:
                continue
        
        raise ValueError(f"Unrecognized date format: {date_str}")
    
    

if __name__=='__main__':
    # cu = CommonUtils()
    user_input = "1983-01-20"  # Example user input
    formatted_date = CommonUtils().convert_date(user_input)
    print(formatted_date)