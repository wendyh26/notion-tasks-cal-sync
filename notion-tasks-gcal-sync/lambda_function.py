import json, os, urllib.request
from datetime import datetime, timedelta

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

def query_notion():
    tasks = []
    cursor = None

    while True:
        # Change the name stating time accordingly based on your own database
        body = {"filter": {"property": "Due", "date": {"is_not_empty": True}}}
        if cursor:
            body["start_cursor"] = cursor

        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read())

        for page in data["results"]:
            # Change the name stating the task accordingly based on your own database
            title_prop = page["properties"].get("Task Name", {}).get("title", [])
            due_prop = page["properties"].get("Due", {}).get("date")
            if not title_prop or not due_prop:
                continue
            tasks.append({
                "id": page["id"].replace("-", ""),
                "title": title_prop[0]["plain_text"],
                "due": due_prop["start"][:10],  # force YYYY-MM-DD, drop any time
                "updated": page["last_edited_time"]
            })

        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]

    return tasks

def to_ics_date(date_str):
    # handles both "YYYY-MM-DD" and ISO datetime strings
    if "T" in date_str:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).strftime("%Y%m%dT%H%M%SZ")
    return date_str.replace("-", "")

def build_ics(tasks):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Notion Sync//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Notion Tasks",
    ]

    for task in tasks:
        due = to_ics_date(task["due"])
        updated = to_ics_date(task["updated"])
        end = (datetime.strptime(due, "%Y%m%d") + timedelta(days=1)).strftime("%Y%m%d")

        lines += [
            "BEGIN:VEVENT",
            f"UID:{task['id']}@notion-sync",
            f"DTSTAMP:{updated}",
            f"LAST-MODIFIED:{updated}",
            f"SUMMARY:{task['title']}",
            f"DTSTART;VALUE=DATE:{due}",
            f"DTEND;VALUE=DATE:{end}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def lambda_handler(event, context):
    try:
        tasks = query_notion()
        ics = build_ics(tasks)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/calendar; charset=utf-8",
                "Cache-Control": "max-age=300"
            },
            "body": ics
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}