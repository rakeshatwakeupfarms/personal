import datetime
from create_events import delete_calendar_event
from list_events import list_events_today

def delete_all_events(calendar_id='raaki.88@gmail.com'):
    print("Getting all events for today to delete...")
    events_to_delete_result = list_events_today(calendar_id=calendar_id)
    if events_to_delete_result["status"] == "success" and events_to_delete_result["events"]:
        print("Deleting all existing events for today...")
        for event in events_to_delete_result["events"]:
            event_id = event.get('id')
            if event_id:
                delete_result = delete_calendar_event(event_id, calendar_id)
                if delete_result["status"] == "success":
                    print(f"  - Deleted: {event['summary']}")
                else:
                    print(f"  - Error deleting {event['summary']}: {delete_result['message']}")
            else:
                print(f"  - Could not delete event '{event['summary']}' (no event ID found).")
    else:
        print("No events found for today to delete.")

if __name__ == '__main__':
    delete_all_events()
