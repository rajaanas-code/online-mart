import requests
from fastapi import HTTPException

MAILGUN_API_KEY = '2b755df8-8653f090'
MAILGUN_DOMAIN = 'sandbox7f0ecbb3b734489db1cc19699f07d611.mailgun.org'
MAILGUN_URL = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages'

def send_email(recipient: str, subject: str, message: str):
    response = requests.post(
        MAILGUN_URL,
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"Raja Anas <mailgun@{MAILGUN_DOMAIN}>",
              "to": recipient,
              "subject": subject,
              "text": message})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)