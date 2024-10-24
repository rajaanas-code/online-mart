from mailjet_rest import Client
from app import settings

def send_email_notification(*, email_to: str, subject: str, email_content_for_send: str) -> None:
    mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": settings.EMAILS_FROM_EMAIL,
                    "Name": settings.EMAILS_FROM_NAME,
                },
                "To": [
                    {
                        "Email": email_to,
                    }
                ],
                "Subject": subject,
                "TextPart": email_content_for_send,
            }
        ]
    }

    response = mailjet.send.create(data=data)
    if response.status_code == 200:
        print(f"Email sent successfully to {email_to}")
    else:
        print(f"Failed to send email. Status code: {response.status_code}")
        print(f"Response: {response.json()}")