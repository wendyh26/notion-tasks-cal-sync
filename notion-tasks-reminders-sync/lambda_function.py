import json
import requests
import os
from datetime import datetime, timedelta

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

NOTION_API_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    try:
        response = requests.post(NOTION_API_URL, headers=HEADERS, json={})
        response.raise_for_status()
        data = response.json()

        tasks = []
        for result in data.get("results", []):
            properties = result.get("properties", {})

            title_data = properties.get("Task Name", {}).get("title", [])
            due_data = properties.get("Due", {}).get("date", {})

            if not title_data or not due_data:
                continue

            title = title_data[0].get("plain_text", "Untitled")
            due = due_data.get("start")

            dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
            if 'T' in due:
                dt_adjust = dt + timedelta(hours=5)
            else:
                dt_adjust = dt + timedelta(hours=27)

            due = dt_adjust.strftime("%Y-%m-%dT%H:%M:%SZ")

            tasks.append({
                "title": title,
                "datetime": due,
            })

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(tasks)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
