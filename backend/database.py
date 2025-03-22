import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Retry logic to wait for database connection
engine = None
for attempt in range(10):
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print("Database connection successful!")
        break
    except OperationalError:
        print(f"Database not ready, retrying ({attempt + 1}/10)...")
        time.sleep(5)
else:
    print("Failed to connect to database after 10 attempts.")
    raise Exception("Database connection failed.")

# Creating a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
