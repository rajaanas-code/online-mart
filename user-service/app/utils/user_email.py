import requests
from fastapi import HTTPException
from app.settings import MAILGUN_API_KEY, MAILGUN_DOMAIN

MAILGUN_URL = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages'

def send_email(recipient: str, subject: str, message: str):
    response = requests.post(
        MAILGUN_URL,
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"User Service <mailgun@{MAILGUN_DOMAIN}>",
              "to": recipient,
              "subject": subject,
              "text": message})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)