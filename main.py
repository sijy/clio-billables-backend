from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Init Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

CLIO_TOKEN = os.getenv("CLIO_TOKEN")

class EmailData(BaseModel):
    body: str
    recipients: list
    duration: float

@app.post("/log-billable")
def log_billable(data: EmailData):
    try:
        summary = get_gemini_summary(data.body)
        contact = find_contact_by_email(data.recipients[0])
        matter = get_matter_for_contact(contact['id'])

        payload = {
            "time_entry": {
                "description": summary,
                "duration": round(data.duration, 1),
                "matter_id": matter["id"],
                "user_id": "me",
                "date": str(date.today()),
                "billable": True
            }
        }

        r = requests.post(
            "https://app.clio.com/api/v4/time_entries",
            headers={"Authorization": f"Bearer {CLIO_TOKEN}"},
            json=payload
        )
        return {"status": r.status_code, "response": r.json()}
    except Exception as e:
        return {"error": str(e)}

def get_gemini_summary(body):
    prompt = f"""
Summarize this email into a professional legal time entry:

Email:
---
{body}
---
Format: Email to [Client] regarding [Topic]. Duration: X minutes.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def find_contact_by_email(email):
    r = requests.get(
        f"https://app.clio.com/api/v4/contacts?query={email}",
        headers={"Authorization": f"Bearer {CLIO_TOKEN}"}
    )
    return r.json()["data"][0]

def get_matter_for_contact(contact_id):
    r = requests.get(
        f"https://app.clio.com/api/v4/matters?client_id={contact_id}",
        headers={"Authorization": f"Bearer {CLIO_TOKEN}"}
    )
    return r.json()["data"][0]
