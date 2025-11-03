"mostly SQLAlchemy models for database tables"
from .database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, String, Boolean, text
from sqlalchemy.sql.expression import null

# Create your models here
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False) #seems primary key autincrements by default
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))