"sqlalchemy database setup and session management"
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#ideally, these would be in environment variables for security
SQALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:Freely-Erased7-Headsman@localhost/APISimulator" #postgres format for sqlalchemy
engine = create_engine(SQALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal() #create a new database session
    try:
        yield db    
    finally:
        db.close()
