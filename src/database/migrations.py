from sqlalchemy import create_engine, Column, Float, text
from sqlalchemy.ext.declarative import declarative_base
from .models import Session
import logging
from ..config import Config
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_variance_columns():
    """Add bb_result and variance columns to sessions table if they don't exist"""
    db_path = os.path.join(Config.APP_DIR, Config.DB_NAME)
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        # Check if columns exist first
        with engine.connect() as conn:
            # Get column info
            columns = conn.execute(text("PRAGMA table_info(sessions)")).fetchall()
            column_names = [col[1] for col in columns]
            
            # Add bb_result if it doesn't exist
            if 'bb_result' not in column_names:
                conn.execute(text('ALTER TABLE sessions ADD COLUMN bb_result FLOAT'))
                logger.info("Added bb_result column")
            
            # Add variance if it doesn't exist
            if 'variance' not in column_names:
                conn.execute(text('ALTER TABLE sessions ADD COLUMN variance FLOAT'))
                logger.info("Added variance column")
                
    except Exception as e:
        logger.error(f"Error managing variance columns: {e}") 