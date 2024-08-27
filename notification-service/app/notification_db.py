from sqlmodel import create_engine, SQLModel

DATABASE_URL = "postgresql+psycopg2://user:password@db/notification_db"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
