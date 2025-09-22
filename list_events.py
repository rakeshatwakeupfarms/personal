import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def list_events_today(calendar_id='primary'):
    """
    Lists events for today from a specified Google Calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This part should ideally not be reached if list_calendars.py already ran and created token.json
            # However, including it for robustness.
            CLIENT_SECRET_FILE = "tokens/client_secret_1090862526299-4j5ntdevkuaicpalm3iqb8dopa2nibnm.apps.googleusercontent.com.json"
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min).isoformat() + 'Z'
        today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max).isoformat() + 'Z'

        print(f'Getting the upcoming events for today from calendar: {calendar_id}...')
        events_result = service.events().list(calendarId=calendar_id, timeMin=today_start, timeMax=today_end,
                                            maxResults=50, singleEvents=True, # Increased maxResults
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return {"status": "success", "events": [], "message": "No upcoming events found for today."}

        event_data = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_data.append({
                "summary": event['summary'],
                "start": start,
                "colorId": event.get('colorId'),
                "id": event.get('id') # Add event ID for deletion
            })
        return {"status": "success", "events": event_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    result = list_events_today(calendar_id='raaki.88@gmail.com') # Using the primary calendar ID from previous run

    if result["status"] == "success":
        if result["events"]:
            print("Today's Schedule:")
            for event in result["events"]:
                color_info = f" (Color ID: {event['colorId']})" if event['colorId'] else ""
                print(f"  - {event['summary']} (Start: {event['start']}){color_info}")
        else:
            print(result["message"])
    else:
        print(f"An error occurred: {result['message']}")
