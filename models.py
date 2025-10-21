import os
from sqlalchemy import Column, String, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE = declarative_base()
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./candidates.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Candidate(BASE):
    __tablename__ = "candidates"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    sections = Column(JSON)
    embeddings = Column(JSON, nullable=True)

def init_db():
    BASE.metadata.create_all(bind=engine)
