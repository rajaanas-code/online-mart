from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=str)
KAFKA_INVENTORY_TOPIC = config("kAFKA_INVENTORY_TOPIC", cast=str)

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY = Config("KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY", cast=str)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)