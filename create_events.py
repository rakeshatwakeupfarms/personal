import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events'] # Scope for creating and modifying events, NOT deleting

def create_calendar_event(summary, start_time_str, end_time_str, calendar_id='primary', description='', color_id=None):
    """
    Creates an event in the specified Google Calendar.

    Args:
        summary (str): The title of the event.
        start_time_str (str): Start time in ISO format (e.g., '2025-09-20T09:00:00+01:00').
        end_time_str (str): End time in ISO format.
        calendar_id (str): The ID of the calendar to add the event to.
        description (str): A description for the event.

    Returns:
        dict: A dictionary containing the status and event details or an error message.
    """
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            CLIENT_SECRET_FILE = "tokens/client_secret_1090862526299-4j5ntdevkuaicpalm3iqb8dopa2nibnm.apps.googleusercontent.com.json"
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time_str,
                'timeZone': 'Europe/Dublin', # Assuming user's timezone based on environment_details
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': 'Europe/Dublin',
            },
        }
        if color_id:
            event['colorId'] = color_id

        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return {"status": "success", "event_id": event.get('id'), "html_link": event.get('htmlLink')}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            CLIENT_SECRET_FILE = "tokens/client_secret_1090862526299-4j5ntdevkuaicpalm3iqb8dopa2nibnm.apps.googleusercontent.com.json"
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    print("Authorization successful. You can now use this script via schedule_day.py.")
