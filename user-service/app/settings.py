from starlette.datastructures import Secret
from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

KAFKA_NOTIFICATION_TOPIC = config("KAFKA_NOTIFICATION_TOPIC", cast=str, default="notification-events")
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str, default="product-events")
