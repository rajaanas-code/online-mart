async def process_notification(notification_data: dict):
    notification_type = notification_data.get("type")
    
    if notification_type == "email":
        await send_email(notification_data)
    elif notification_type == "sms":
        await send_sms(notification_data)
    else:
        print("Unknown notification type")

async def send_email(notification_data: dict):
    recipient = notification_data.get("recipient")
    message = notification_data.get("message")
    # Logic to send email
    print(f"Sending email to {recipient}: {message}")

async def send_sms(notification_data: dict):
    recipient = notification_data.get("recipient")
    message = notification_data.get("message")
    # Logic to send SMS
    print(f"Sending SMS to {recipient}: {message}")
