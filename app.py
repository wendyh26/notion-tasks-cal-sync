from flask import Flask, request
from notion import get_page_detail
from pushcut import send_task_to_pushcut
from config import VERIFICATION_TOKEN

app = Flask(__name__)

@app.route("/notion-webhook", methods=["POST"])
def webhook():
    # 安全验证
    if request.headers.get("Notion-Webhook-Verify-Token") != VERIFICATION_TOKEN:
        return "Unauthorized", 403

    data = request.json
    for event in data.get("event_data", []):
        page_id = event.get("id")
        detail = get_page_detail(page_id)

        props = detail["properties"]
        title = props["Title"]["title"][0]["plain_text"]
        due = props["Due"]["date"]["start"]

        send_task_to_pushcut(title, due)

    return "OK", 200
