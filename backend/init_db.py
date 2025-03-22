from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Import your Base model from your models file
import os
from dotenv import load_dotenv

load_dotenv()

# Update the DATABASE_URL to use localhost
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # This will create the tables defined in your models
