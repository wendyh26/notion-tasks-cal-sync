# Notion Tasks GCal/Reminder Sync

This repo tutorial teaches how to ✅: 

1.  Syncs tasks from a Notion database to Google Calendar as all-day events, via a subscribable ICS feed hosted on AWS Lambda 📅. 
2. tbd

## What It Does

Exposes a URL that returns a live `.ics` calendar feed generated from your Notion database. Any task with a due date is included as an all-day event. Google Calendar (or any calendar app that supports ICS subscriptions) can subscribe to this URL and automatically stay in sync.

## Prerequisites

- A [Notion](https://notion.so) account with a database that has a **title column** and a **date column**
- An [AWS account](https://aws.amazon.com/free) (free tier is sufficient)


## Step 1: Get Your Notion Credentials

### Integration Token

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **New integration**, give it a name, select your workspace
3. Copy the **Internal Integration Secret** (starts with `ntn_...`)

### Connect Integration to Your Database

1. Open your Notion database
2. Click **...** (top right) → **Connections** → find your integration and connect it

### Database ID

Open your Notion database in the browser. The URL looks like:
```
https://www.notion.so/myworkspace/83b5e4a1c2df4f8b9a0e1234567890ab?v=...
```
The database ID is the 32-character hex string before `?v=`. In this example: `83b5e4a1c2df4f8b9a0e1234567890ab`.


## Step 2: Set Up AWS Lambda

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda) → **Create function**
2. Select **Author from scratch**
3. Name: `notion-ics-sync`, Runtime: **Python 3.12**
4. Click **Create function**


## Step 3: Deploy the Code

Copy the code from [`notion-tasks-gcal-sync/lambda_function.py`](notion-tasks-gcal-sync/lambda_function.py) and paste it into the Lambda inline code editor, then click **Deploy**.

> **Important:** Check your Notion database column names and update `"Name"` and `"Due"` in the code to match exactly.


## Step 4: Set Environment Variables

1. Go to **Configuration → Environment variables → Edit**
2. Add the following:

| Key | Value |
|---|---|
| `NOTION_TOKEN` | Your integration secret (`ntn_...`) |
| `DATABASE_ID`  | Your 32-character database ID |

3. Click **Save**


## Step 5: Create a Function URL

1. Go to **Configuration → Function URL → Create function URL**
2. Auth type: **NONE**
3. Click **Save**
4. Copy the generated URL (looks like `https://xxxx.lambda-url.us-east-1.on.aws/`)


## Step 6: Test

1. Go to the **Test** tab in Lambda
2. Create a new test event with this body:

```json
{
  "requestContext": {
    "http": { "method": "GET" }
  },
  "rawPath": "/",
  "rawQueryString": ""
}
```

3. Click **Test** and expand the result

**Success:** The response body starts with `BEGIN:VCALENDAR` and contains `BEGIN:VEVENT` blocks for each task.

You can also paste the Function URL directly in your browser — it should trigger a `.ics` file download. Open it in a text editor to verify your tasks appear correctly.


## Step 7: Subscribe in Google Calendar

1. Open [Google Calendar](https://calendar.google.com)
2. Click **+** next to **Other calendars** in the left sidebar
3. Select **From URL**
4. Paste your Lambda Function URL
5. Click **Add calendar**

A new calendar called **Notion Tasks** will appear. Google Calendar polls the feed every 6–24 hours automatically.

> To force an immediate refresh, remove the calendar and re-add it.


## Notes

- Only tasks with a due date set in Notion are synced
- All events are all-day — no specific time is attached
- If your Notion column names differ from `Name` and `Due`, update those strings in the Lambda code
- AWS Lambda free tier covers 1M requests/month — this will never cost anything at this usage level


## Acknowledgements
 
**Author:** Wendy Huang  
All rights reserved. Unauthorized copying, reproduction, or distribution of this project or any of its contents is strictly prohibited.
 
*Built with assistance from [Claude](https://claude.ai) by Anthropic.*