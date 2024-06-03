import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
from datetime import datetime, timedelta

# Twilio account credentials
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
twilio_phone_number = 'your_twilio_phone_number'

# Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_json_keyfile', scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open('your_sheet_name').sheet1

# Get all the data from the sheet
data = sheet.get_all_values()

# Iterate through the data (excluding the header row)
for row in data[1:]:
    # Assuming the date is in the first column and "converted" status is in the second column
    date_str = row[0]
    converted = row[1]
    
    # Parse the date string into a datetime object
    entry_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Check if the entry is older than 48 hours and not converted
    if entry_date < datetime.now() - timedelta(hours=48) and converted.lower() != 'yes':
        # Send a text message using Twilio
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Entry from {date_str} has been unconverted for more than 48 hours.",
            from_=twilio_phone_number,
            to='recipient_phone_number'
        )
        print(f"Text message sent for entry dated {date_str}")


