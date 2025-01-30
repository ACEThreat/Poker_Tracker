from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
import logging

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
