from sqlmodel import create_engine
from app import settings

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg2"
)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)
