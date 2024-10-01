from app.settings import DATABASE_URL
from sqlmodel import create_engine

connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)