from starlette.datastructures import Secret
from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str, default="order-events")
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str, default="product-events")

STRIPE_API_KEY = config("STRIPE_API_KEY", cast=str)