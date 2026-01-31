from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class Conversion(Base):
    __tablename__ = "conversions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    source_format = Column(String)
    target_format = Column(String)
    file_size = Column(Float)  # in MB
    status = Column(String)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
