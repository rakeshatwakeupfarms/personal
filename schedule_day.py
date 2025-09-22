import re
import datetime
import sys
from create_events import create_calendar_event
from list_events import list_events_today # Import the function to list existing events

def parse_checklist_and_schedule(checklist_path, calendar_id='raaki.88@gmail.com'):
    """
    Parses a markdown checklist, extracts tasks with time blocks, and schedules them as Google Calendar events.
    It only schedules tasks that are not already present in the calendar and applies a specific color to new tasks.
    """
    # Get existing events for today
    existing_events_result = list_events_today(calendar_id=calendar_id)
    existing_event_summaries = set()
    if existing_events_result["status"] == "success" and existing_events_result["events"]:
        for event in existing_events_result["events"]:
            existing_event_summaries.add(event["summary"])

    # Dynamically determine the date from the checklist filename
    try:
        date_str = re.search(r'(\d{4}-\d{2}-\d{2})', checklist_path).group(1)
        today = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (AttributeError, ValueError):
        print("Could not determine date from filename. Using today's date.")
        today = datetime.date.today()

    with open(checklist_path, 'r') as f:
        content = f.read()

    # Regex to find lines with unchecked tasks and time blocks
    # Example: - [ ] **Task Name**: HH:MM-HH:MM Description
    task_pattern = re.compile(r'^- \[ \] \*\*(.*?)\*\*: (\d{2}:\d{2})-(\d{2}:\d{2}) (.*)')

    scheduled_events = []
    for line in content.splitlines():
        match = task_pattern.match(line)
        if match:
            summary = match.group(1).strip()
            start_time_str = match.group(2)
            end_time_str = match.group(3)
            description = match.group(4).strip()

            # Only schedule if the event is not already in the calendar
            if summary not in existing_event_summaries:
                # Combine date and time
                start_datetime = datetime.datetime.combine(today, datetime.datetime.strptime(start_time_str, '%H:%M').time())
                end_datetime = datetime.datetime.combine(today, datetime.datetime.strptime(end_time_str, '%H:%M').time())

                # Format for Google Calendar API (ISO 8601 with timezone)
                # Assuming Europe/Dublin timezone based on previous context
                start_iso = start_datetime.isoformat() + '+01:00' # UTC+1:00 for Europe/Dublin
                end_iso = end_datetime.isoformat() + '+01:00'

                color_id_to_use = '6' # Google Calendar color ID for orange for new events

                print(f"Scheduling: {summary} from {start_iso} to {end_iso} (Color ID: {color_id_to_use})")
                event_result = create_calendar_event(summary, start_iso, end_iso, calendar_id, description, color_id=color_id_to_use)

                if event_result["status"] == "success":
                    scheduled_events.append(f"'{summary}' (Link: {event_result['html_link']})")
                else:
                    print(f"Error scheduling '{summary}': {event_result['message']}")
            else:
                print(f"Event '{summary}' already exists in calendar. Skipping.")

    return scheduled_events

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python schedule_day.py <path_to_checklist_file>")
        sys.exit(1)

    checklist_file = sys.argv[1]
    print(f"Scheduling events from {checklist_file}...")
    events = parse_checklist_and_schedule(checklist_file)

    if events:
        print("\nSuccessfully scheduled the following events:")
        for event in events:
            print(f"- {event}")
    else:
        print("\nNo new events were scheduled.")
