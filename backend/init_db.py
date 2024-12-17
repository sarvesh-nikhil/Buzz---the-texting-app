from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Import your Base model from your models file

# Update the DATABASE_URL to use localhost
DATABASE_URL = "mysql+pymysql://root:student@localhost:3306/Chatappusers"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # This will create the tables defined in your models
