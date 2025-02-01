import os
from pathlib import Path

class Config:
    APP_DIR = os.path.expanduser('~/.poker_tracker')
    DB_NAME = 'database.db'
    LOG_DIR = os.path.join(APP_DIR, 'logs')
    IMPORT_DIR = os.path.join(APP_DIR, 'DB_Import_Files')
    CHROME_PROFILE = '/Users/shane/Library/Application Support/Google/Chrome'
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.APP_DIR, cls.LOG_DIR, cls.IMPORT_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True) 