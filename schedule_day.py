import re
import datetime
import sys
import pytz # Import pytz for timezone handling
from create_events import create_calendar_event
from list_events import list_events_today # Import the function to list existing events

def parse_checklist_and_schedule(checklist_path, calendar_id='raaki.88@gmail.com'):
    """
    Parses a markdown checklist, extracts tasks with time blocks, and schedules them as Google Calendar events.
    It only schedules tasks that are not already present in the calendar and applies a specific color to new tasks.
    """
    # Get existing events for today
    existing_events_result = list_events_today(calendar_id=calendar_id)
    existing_events = []
    if existing_events_result["status"] == "success" and existing_events_result["events"]:
        for event in existing_events_result["events"]:
            # Parse existing event times into datetime objects for comparison
            try:
                event_start = datetime.datetime.fromisoformat(event["start"].replace('Z', '+00:00'))
                event_end = datetime.datetime.fromisoformat(event["end"].replace('Z', '+00:00'))
                existing_events.append({
                    "summary": event["summary"],
                    "start": event_start,
                    "end": event_end
                })
            except ValueError:
                print(f"Warning: Could not parse datetime for existing event '{event['summary']}'. Skipping for overlap check.")
                continue

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

            # Combine date and time for new task
            new_task_start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
            new_task_end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
            
            # Combine date and time, then localize to Europe/Dublin timezone
            dublin_tz = pytz.timezone('Europe/Dublin')
            new_task_start_datetime = dublin_tz.localize(datetime.datetime.combine(today, new_task_start_time))
            new_task_end_datetime = dublin_tz.localize(datetime.datetime.combine(today, new_task_end_time))

            # Check for overlaps with existing events
            overlap_found = False
            for existing_event in existing_events:
                # Check if new task starts during existing event
                if existing_event["start"] < new_task_start_datetime < existing_event["end"]:
                    overlap_found = True
                    print(f"Skipping '{summary}': Overlaps with existing event '{existing_event['summary']}' ({existing_event['start'].strftime('%H:%M')}-{existing_event['end'].strftime('%H:%M')}).")
                    break
                # Check if new task ends during existing event
                if existing_event["start"] < new_task_end_datetime < existing_event["end"]:
                    overlap_found = True
                    print(f"Skipping '{summary}': Overlaps with existing event '{existing_event['summary']}' ({existing_event['start'].strftime('%H:%M')}-{existing_event['end'].strftime('%H:%M')}).")
                    break
                # Check if existing event starts during new task
                if new_task_start_datetime < existing_event["start"] < new_task_end_datetime:
                    overlap_found = True
                    print(f"Skipping '{summary}': Overlaps with existing event '{existing_event['summary']}' ({existing_event['start'].strftime('%H:%M')}-{existing_event['end'].strftime('%H:%M')}).")
                    break
                # Check if new task completely encompasses existing event
                if new_task_start_datetime <= existing_event["start"] and new_task_end_datetime >= existing_event["end"]:
                    overlap_found = True
                    print(f"Skipping '{summary}': Overlaps with existing event '{existing_event['summary']}' ({existing_event['start'].strftime('%H:%M')}-{existing_event['end'].strftime('%H:%M')}).")
                    break
                # Check for exact start/end time match (duplicate summary already handled by existing_event_summaries)
                if new_task_start_datetime == existing_event["start"] and new_task_end_datetime == existing_event["end"]:
                    overlap_found = True
                    print(f"Skipping '{summary}': Exact time match with existing event '{existing_event['summary']}'.")
                    break

            if not overlap_found:
                # Format for Google Calendar API (ISO 8601 with timezone)
                # The datetime objects are already localized, so isoformat() will include the timezone offset.
                start_iso = new_task_start_datetime.isoformat()
                end_iso = new_task_end_datetime.isoformat()

                color_id_to_use = '6' # Google Calendar color ID for orange for new events

                print(f"Scheduling: {summary} from {start_iso} to {end_iso} (Color ID: {color_id_to_use})")
                event_result = create_calendar_event(summary, start_iso, end_iso, calendar_id, description, color_id=color_id_to_use)

                if event_result["status"] == "success":
                    scheduled_events.append(f"'{summary}' (Link: {event_result['html_link']})")
                    # Add newly scheduled event to existing_events for subsequent overlap checks within the same run
                    existing_events.append({
                        "summary": summary,
                        "start": new_task_start_datetime,
                        "end": new_task_end_datetime
                    })
                else:
                    print(f"Error scheduling '{summary}': {event_result['message']}")
            else:
                # If overlap found, it was already printed, so just continue
                pass

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
