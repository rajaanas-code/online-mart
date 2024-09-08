import mailjet_rest
from app.settings import MAILJET_API_KEY, MAILJET_SECRET_KEY

def send_email(recipient: str, subject: str, message: str, image_url: str) -> None:
    mailjet = mailjet_rest.Client(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), version='v3.1')
    
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "rajaanasturk157@gmail.com",
                    "Name": "Online Mart API"
                },
                "To": [
                    {
                        "Email": recipient,
                        "Name": "Online Mart API"
                    }
                ],
                "Subject": subject,
                "TextPart": message,
                "HTMLPart": f"""
                    <h3>{subject}</h3>
                    <p>{message}</p>
                    <img src="{image_url}" alt="Image" width="300px" height="auto"/>
                """,
            }
        ]
    }
    
    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        raise Exception(f"Failed to send email: {result.status_code} {result.reason}")