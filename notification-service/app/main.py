import asyncio
from app.notification_consumer import consume_notification_events

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_notification_events())
