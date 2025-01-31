from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from ..database.database import Database
import time
import logging
import os
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
from ..scraping.session_parser import SessionParser
from ..database.session_importer import SessionImporter
import re

class SessionScraper:
    def __init__(self):
        self.driver = None
        self.page_text = None
        self.verification_result = False
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
        """Extract page content after login and show in popup for verification"""
        try:
            def parse_and_format_content(content):
                # Parse the content using regex
                table_entries = re.finditer(
                    r"(Jan \d{1,2}, \d{1,2}:\d{2} [APM]{2})\n"  # Date and time
                    r"((?:\d+h )?\d+m \d+s)\n"  # Duration
                    r"(Hold'em|Omaha)\n"  # Game format
                    r"([\d.]+ SC / [\d.]+ SC)\n"  # Stakes
                    r"(\d+)\n"  # Hands played
                    r"([+-][\d.]+ SC)",  # Result
                    content
                )
                
                parsed_sessions = []
                formatted_text = "=== Parsed Sessions ===\n\n"
                
                for match in table_entries:
                    start_time_str = match.group(1)
                    duration = match.group(2)
                    game_format = match.group(3)
                    stakes = match.group(4)
                    hands_played = int(match.group(5))
                    result = float(match.group(6).replace(" SC", ""))

                    # Parse start time
                    start_time = datetime.strptime(start_time_str, "%b %d, %I:%M %p")
                    start_time = start_time.replace(year=datetime.now().year)
                    
                    session = {
                        'start_time': start_time,
                        'duration': duration,
                        'game_format': game_format,
                        'stakes': stakes,
                        'hands_played': hands_played,
                        'result': result
                    }
                    parsed_sessions.append(session)
                    
                    formatted_text += (
                        f"Start time ({start_time.strftime('%b %d, %I:%M %p')}) "
                        f"Duration ({duration}) "
                        f"Format ({game_format}) "
                        f"Stake ({stakes}) "
                        f"HandsPlayed ({hands_played}) "
                        f"Result ({result:+.2f} SC)\n"
                    )
                
                formatted_text += "\n=== Raw Content ===\n\n" + content
                return formatted_text, parsed_sessions
            
            def show_verification_window(content):
                popup = tk.Tk()
                popup.title("Scraped Content Verification")
                popup.geometry("800x600")
                
                # Add scrollable text area
                text_area = scrolledtext.ScrolledText(popup, width=80, height=30)
                text_area.pack(padx=10, pady=10, expand=True, fill='both')
                
                # Parse and show formatted content
                formatted_content, parsed_sessions = parse_and_format_content(content)
                text_area.insert(tk.END, formatted_content)
                
                # Button functions
                def verify():
                    try:
                        importer = SessionImporter()
                        success, message = importer.import_sessions(parsed_sessions)
                        if success:
                            messagebox.showinfo("Success", f"Successfully imported {len(parsed_sessions)} sessions")
                            self.verification_result = True
                            self.page_text = content  # Save the raw content
                        else:
                            messagebox.showerror("Import Error", f"Failed to import sessions: {message}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error during import: {str(e)}")
                
                def new_scrape():
                    popup.destroy()
                    new_content = self.driver.execute_script("return document.body.innerText;")
                    show_verification_window(new_content)
                
                def retry():
                    popup.destroy()
                    new_content = self.driver.execute_script("return document.body.innerText;")
                    show_verification_window(new_content)
                
                def close_browser():
                    if messagebox.askyesno("Confirm Close", "Are you sure you want to close the browser?"):
                        self.driver.quit()
                        popup.destroy()
                
                def cancel():
                    if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel? This will close the browser."):
                        self.verification_result = False
                        self.page_text = None
                        self.driver.quit()
                        popup.destroy()
                
                # Button frame
                button_frame = tk.Frame(popup)
                button_frame.pack(pady=10)
                
                # Add buttons
                tk.Button(button_frame, text="Verify & Import", command=verify).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="New Scrape", command=new_scrape).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Retry Current", command=retry).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Close Browser", command=close_browser).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
                
                popup.mainloop()
            
            # Initial scrape
            self.verification_result = False
            initial_content = self.driver.execute_script("return document.body.innerText;")
            show_verification_window(initial_content)
            
            return self.verification_result
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