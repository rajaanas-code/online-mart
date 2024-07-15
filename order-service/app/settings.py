from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)

BOOTSTRAP_SERVERS = config("BOOTSTRAP_SERVERS", cast=str)
