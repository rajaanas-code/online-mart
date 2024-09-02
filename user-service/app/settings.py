from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str, default="user-events")
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str, default="product-events")
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str, default="order-events")
KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", cast=str, default="payment-events")
KAFKA_NOTIFICATION_TOPIC = config("KAFKA_NOTIFICATION_TOPIC", cast=str, default="notification-events")

SECRET_KEY = config("SECRET_KEY", cast=Secret)
ALGORITHM = "HS256"