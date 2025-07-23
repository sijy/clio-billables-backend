from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

CLIENT_ID = os.getenv("CLIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("CLIO_REDIRECT_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

clio_token = None  # In-memory for MVP

@app.get("/auth/clio/login")
def auth_redirect():
    url = f"https://app.clio.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=read:contacts read:matters write:time_entries"
    return {"url": url}

@app.get("/auth/clio/callback")
def auth_callback(code: str):
    global clio_token
    token_url = "https://app.clio.com/oauth/token"
    res = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    })
    clio_token = res.json()["access_token"]
    return {"message": "Token received"}

class EmailData(BaseModel):
    body: str
    seconds: int

@app.post("/api/log")
def log_email(data: EmailData):
    global clio_token
    minutes = round(data.seconds / 60, 2)
    
    # Step 1: Use Gemini to summarize
    summary = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY,
        json={"contents": [{"parts": [{"text": f"Summarize this email into a time entry: {data.body}"}]}]}
    ).json()["candidates"][0]["content"]["parts"][0]["text"]

    # Step 2: Log to Clio (dummy matter_id for now)
    res = requests.post(
        "https://app.clio.com/api/v4/time_entries",
        headers={"Authorization": f"Bearer {clio_token}"},
        json={
            "time_entry": {
                "description": summary,
                "duration": int(data.seconds),
                "matter_id": "your_matter_id_here"
            }
        }
    )
    return {"summary": summary, "minutes": minutes, "clio_response": res.json()}
