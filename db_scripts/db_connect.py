from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from configs.db_config import settings
from logger import logging


class Base(DeclarativeBase):
    pass


try:
    engine = create_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
except Exception as e:
    logging.error(f"Error while creating SQLAlchemy engine: {e}")
    raise
    

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        


if __name__ == "__main__":

    try:

        with engine.connect() as conn:

            result = conn.execute(text("SELECT 1"))

            print(result.scalar())

        print("Database connection successful!")

    except Exception as e:

        print(f"Connection failed: {e}")