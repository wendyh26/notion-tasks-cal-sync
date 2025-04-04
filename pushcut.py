# pushcut.py
import requests
import json
from config import PUSHCUT_WEBHOOK_URL

def send_task_to_pushcut(title, datetime_str):
    task_data = {
        "title": title,
        "datetime": datetime_str
    }
    url = PUSHCUT_WEBHOOK_URL + requests.utils.quote(json.dumps(task_data, ensure_ascii=False))
    response = requests.get(url)
    print(f"[Pushcut] Sent task to iPhone: {task_data}")
    print(f"[Pushcut] Response: {response.status_code}")
