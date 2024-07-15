from sqlmodel import create_engine
from app.settings import DATABASE_URL

connection_string = str(DATABASE_URL).replace("postgresql", "postgresql+psycopg2")

engine = create_engine(connection_string)