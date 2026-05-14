# Notion Tasks GCal/Reminder Sync

This repo tutorial teaches how to sync your Notion tasks to your calendars and reminders. Choose a guide: ✅ 

- [Part 1: Sync Notion Tasks → Google Calendar 📅](#part-1-sync-notion-tasks--google-calendar-)
- [Part 2: Sync Notion Tasks → Apple Reminders 🍎](#part-2-sync-notion-tasks--apple-reminders-)

---

## Part 1: Sync Notion Tasks → Google Calendar 📅
 
Syncs tasks from a Notion database to Google Calendar as all-day events, via a subscribable ICS feed hosted on AWS Lambda.

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

> **Important:** Check your Notion database column names and update `Task Name` and `Due` in the code to match exactly. Make sure each task name and due date is not empty.


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

---

## Part 2: Sync Notion Tasks → Apple Reminders 🍎 

Syncs tasks from a Notion database to Apple Reminders using AWS Lambda + API Gateway as a backend, triggered manually via an iOS Shortcut.


## What It Does
 
An iOS Shortcut calls your API Gateway endpoint, which triggers a Lambda function that reads your Notion database and returns a list of tasks with due dates. The Shortcut then loops through the results and adds each task to a Reminders list called **Notion**. A notification confirms success or failure.


## Prerequisites
 
- Same Notion integration token and database ID from Part 1
- An AWS account (free tier)
- An iPhone with the **Shortcuts** app
- A Reminders list on your iPhone named exactly **Notion** (create it manually in the Reminders app first)
- Your Notion database must have a task title column (named `Task Name`) and a due date column (named `Due`)
> If your column names differ, update `"Task Name"` and `"Due"` in the Lambda code to match.


## Step 1: Create the Lambda Function
 
1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda) → **Create function**
2. Select **Author from scratch**
3. Name: `notion-reminders-sync`, Runtime: **Python 3.12**
4. Click **Create function**


## Step 2: Add the `requests` Dependency

Unlike Part 1, this Lambda uses the `requests` library which isn't built into Python. You need to package it:

```bash
mkdir package && cd package
pip install requests -t .
cp ../lambda_function.py .
zip -r ../function.zip .
```

Then upload `function.zip` via **Code → Upload from → .zip file** in the Lambda console.
 
Alternatively, add a Lambda Layer for `requests` — search for a public `requests` layer in your region.

 
## Step 3: Deploy the Code
 
The code is in [`notion-tasks-reminders-sync/lambda_function.py`](notion-tasks-reminders-sync/lambda_function.py).
 
> **Important:** Update `Task Name` and `Due` in the code if your Notion column names differ.
 
 
## Step 4: Set Environment Variables
 
1. Go to **Configuration → Environment variables → Edit**
2. Add:

| Key | Value |
|---|---|
| `NOTION_TOKEN` | Your integration secret (`ntn_...`) |
| `DATABASE_ID` | Your 32-character Notion database ID |
 
3. Click **Save**

 
## Step 5: Set Up API Gateway
 
1. Go to **Configuration → Triggers → Add trigger**
2. Select **API Gateway**
3. Choose **Create a new API**, type **HTTP**, security **Open**
4. Click **Add**
5. Copy the **API endpoint URL** — looks like `https://xxxx.execute-api.us-east-2.amazonaws.com/default/NotionTaskSync`

 
## Step 6: Test the Lambda
 
1. Go to the **Test** tab
2. Create a test event with an empty body:
```json
{}
```
3. Click **Test**
**Success:** Response has `statusCode: 200` and the body contains a JSON array of your tasks:
```json
[
  {"title": "CS HW", "datetime": "2026-05-20T03:00:00Z"},
  ...
]
```
 
If you see `statusCode: 500`, check CloudWatch logs under **Monitor → View CloudWatch logs**.

 
## Step 7: Set Up the iOS Shortcut
 
1. Download the Shortcut file: [`notion_sync.shortcut`](notion-tasks-reminders-sync/notion_sync.shortcut)
2. Open it on your iPhone — it will open in the Shortcuts app
3. Find the **Get URL** step and replace the URL with your own API Gateway endpoint from Step 5
4. Save the Shortcut
The Shortcut does the following:
- Clears existing reminders in your **Notion** list to avoid duplicates
- Calls your API Gateway URL to fetch tasks
- Loops through each task and adds it to the **Notion** Reminders list with the due date
- Shows a **"Notion Tasks Synced Successfully ✅"** notification on completion, or an error notification if something went wrong


## Step 8: Test the Shortcut
 
1. Open the Shortcuts app and run **Notion Sync** (or whatever you renamed it)
2. If successful, you'll see a notification: **Notion Tasks Synced Successfully ✅**
3. Open your Reminders app → **Notion** list — your tasks should appear with due dates
If you see an error notification, verify:
- The API Gateway URL in the Shortcut matches exactly what's in AWS
- The **Notion** reminders list exists on your device
- The Lambda test returns `statusCode: 200`


## Notes
 
- This sync is **manual** — run the Shortcut whenever you want to pull the latest tasks. You can also add it to an automation in Shortcuts to run on a schedule.
- **Tasks missing either a title or a due date will be skipped** — make sure both fields are filled in for every task you want synced
- **Before running the Shortcut for the first time, make sure your Notion reminders list is empty.** On subsequent runs, the Shortcut automatically checks for duplicate reminders and deletes them before re-adding, so you won't end up with repeated tasks
- The Lambda adjusts due datetimes by +5 hours (datetime) or +27 hours (date-only) to account for timezone offset — adjust the `timedelta` values in the code if your timezone differs than CST
 
---

## Acknowledgements
 
**Author:** Wendy Huang  
All rights reserved. Unauthorized copying, reproduction, or distribution of this project or any of its contents is strictly prohibited.
 
*Built with assistance from [Claude](https://claude.ai) by Anthropic.*