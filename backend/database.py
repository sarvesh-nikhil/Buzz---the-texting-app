# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL Database URL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:student@localhost/Chatappusers"

# Creating the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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
