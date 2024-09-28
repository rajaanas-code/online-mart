from starlette.datastructures import Secret
from starlette.config import Config

config = Config(".env")

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
DATABASE_URL = config("DATABASE_URL", cast=Secret)

KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str, default="order-events")
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str,  default="product-events")