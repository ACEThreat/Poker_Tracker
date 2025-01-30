from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base, Session
import os
import logging
from datetime import datetime, timedelta

class Database:
    @staticmethod
    def get_app_directory():
        """Get the application directory path"""
        app_dir = os.path.expanduser('~/.poker_tracker')
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        return app_dir

    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Get app directory and database path
        app_dir = self.get_app_directory()
        db_path = os.path.join(app_dir, 'database.db')
        
        # Create database engine
        try:
            self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
            
            # Check if tables exist using inspect
            inspector = inspect(self.engine)
            if not inspector.has_table('sessions'):
                self.logger.info(f"Creating database tables at: {db_path}")
                Base.metadata.create_all(self.engine)
                self.logger.info("Database tables created successfully")
            else:
                self.logger.info(f"Using existing database at: {db_path}")
                
        except Exception as e:
            self.logger.error(f"Error with database: {e}")
            raise
            
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
    
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
