from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    room = Column(String)
    start_time = Column(DateTime)
    duration = Column(String)
    game_format = Column(String)
    stakes = Column(String)
    hands_played = Column(Integer)
    result = Column(Float)
    total_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    bb_result = Column(Float)  # Result in big blinds
    variance = Column(Float)   # Variance for this session
