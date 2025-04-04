# notion.py
import requests
from config import NOTION_TOKEN

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def get_page_detail(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    res = requests.get(url, headers=headers)
    return res.json()
