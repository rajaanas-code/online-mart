from sqlmodel import create_engine
from app.settings import settings

connection_string = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg2")

engine = create_engine(connection_string, connect_args={"options": "-c timezone=utc"}, pool_recycle=3000)
