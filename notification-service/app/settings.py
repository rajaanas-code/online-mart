from starlette.datastructures import Secret
from starlette.config import Config

config = Config(".env")

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str, default="order-events")
MAILJET_API_KEY = config("MAILJET_API_KEY", cast=str)
MAILJET_SECRET_KEY = config("MAILJET_SECRET_KEY", cast=str)