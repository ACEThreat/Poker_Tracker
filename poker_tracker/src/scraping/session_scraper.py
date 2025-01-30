from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from ..database.database import Database
import time
import logging
import os
from datetime import datetime

class SessionScraper:
    def __init__(self):
        self.driver = None
        self.page_text = None
        self.setup_logging()
        
    def setup_logging(self):
        app_dir = Database.get_app_directory()
        log_dir = os.path.join(app_dir, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'session_scraper_{timestamp}.log')
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SessionScraper')

    def initialize_driver(self):
        """Initialize Chrome driver with default profile"""
        options = webdriver.ChromeOptions()
        options.add_argument('--user-data-dir=/Users/shane/Library/Application Support/Google/Chrome')
        options.add_argument('--profile-directory=Default')
        options.add_argument('--start-maximized')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return True

    def navigate_to_url(self, url):
        """Navigate to the specified URL"""
        try:
            self.driver.get(url)
            # Wait for page to fully load
            wait = WebDriverWait(self.driver, 10)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            time.sleep(3)  # Additional wait for AJAX content
            return True
        except Exception as e:
            self.logger.error(f"Navigation error: {str(e)}")
            return False

    def get_page_content(self):
        """Extract page content after login"""
        try:
            self.page_text = self.driver.execute_script("return document.body.innerText;")
            return True
        except Exception as e:
            self.logger.error(f"Content extraction error: {str(e)}")
            return False

    def save_content(self):
        """Save the scraped content to file"""
        if not self.page_text:
            return None
            
        app_dir = Database.get_app_directory()
        output_dir = os.path.join(app_dir, "DB_Import_Files")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(output_dir, f'page_content_{timestamp}.txt')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.page_text)
            return filename
        except Exception as e:
            self.logger.error(f"Save error: {str(e)}")
            return None

    def cleanup(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.driver = None 