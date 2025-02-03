from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base, Session
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.pool import QueuePool
from .migrations import add_variance_columns
from ..config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    @staticmethod
    def get_app_directory():
        """Get the application directory path"""
        app_dir = os.path.expanduser('~/.poker_tracker')
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        return app_dir

    def __init__(self):
        """Initialize database connection and run migrations"""
        self.db_path = os.path.join(Config.APP_DIR, Config.DB_NAME)
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Run migrations
        add_variance_columns()
        
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Using existing database at: {self.db_path}")

    def get_session(self):
        return self.Session()

    def update_total_hours(self):
        """Update total_hours for all sessions"""
        session = self.get_session()
        try:
            # Get all sessions ordered by start time
            sessions = session.query(Session).order_by(Session.start_time).all()
            current_total_hours = 0
            current_end = None
            
            for s in sessions:
                # Parse duration to hours
                duration_parts = s.duration.split()
                duration_hours = 0
                for part in duration_parts:
                    if part.endswith('h'):
                        duration_hours += float(part[:-1])
                    elif part.endswith('m'):
                        duration_hours += float(part[:-1]) / 60
                    elif part.endswith('s'):
                        duration_hours += float(part[:-1]) / 3600
                
                start = s.start_time
                end = start + timedelta(hours=duration_hours)
                
                if current_end is None:
                    current_total_hours += duration_hours
                else:
                    if start > current_end:
                        current_total_hours += duration_hours
                    else:
                        if end > current_end:
                            current_total_hours += (end - current_end).total_seconds() / 3600
                
                current_end = max(end, current_end) if current_end else end
                s.total_hours = current_total_hours
            
            session.commit()
        finally:
            session.close()
