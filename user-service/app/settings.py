from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=Secret)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)

