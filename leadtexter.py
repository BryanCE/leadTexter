import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# we need these modules to send the emails if we decide to
import smtplib
import ssl
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from datetime import datetime, timedelta

def get_phone_number_by_name(agents, name):
    for agent in agents:
        if agent['name'].lower() == name.lower():
            return agent['phone_number']
    return None

def main():
    #------------------------------------ GATHER CREDENTIALS/STARTUP ------------------------------------#
    # Load Twilio credentials from
    with open('twilio_creds.json') as f:
        twilio_creds = json.load(f)

    account_sid = twilio_creds['test_account_sid']
    auth_token = twilio_creds['test_auth_token']
    twilio_phone_number = twilio_creds['phone_number']

    # Load agent phone numbers
    with open('agent_numbers.json') as f:
        agents = json.load(f)

    # Google Sheets credentials
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('leadtexter-425305-fa934534827b.json', scope)
    gc = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = gc.open('2025 SDR Leads').sheet1
    #------------------------------------ END GATHER CREDENTIALS/STARTUP ------------------------------------#




    # Get all the data from the sheet
    data = sheet.get_all_values()

    # Iterate through the data (excluding the header row)
    for row in data[1:]:
        lead_name = row[0]
        lead_email = row[1]
        date_str = row[2]
        assigned_agent = row[3]
        converted = row[4]
        
        # Parse the date string into a datetime object
        entry_date = datetime.strptime(date_str, '%m/%d/%Y')
        
        # Check if the entry is older than 48 hours and not converted
        if entry_date < datetime.now() - timedelta(hours=48) and converted.lower() != 'yes':
            #get the agents phone number based on sheet data
            agent_phone_number = get_phone_number_by_name(agents, assigned_agent)
        try:
            # Send a text message using Twilio
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=f"Your lead with {lead_name}, given to you on {date_str} is still unconverted! Please follow up with them. Email: {lead_email}",
                from_=twilio_phone_number,
                to=agent_phone_number
            )
            print(f"Text message sent to {assigned_agent} for lead with {lead_name}!")
        except TwilioRestException as e:
            print(f"Error sending text message to {assigned_agent} for lead with {lead_name}!: {str(e)}")
        except Exception as e:
            print(f"Error sending text message to {assigned_agent} for lead with {lead_name}!: {str(e)}")


if __name__ == "__main__":
    main()
    print("Script executed successfully.")