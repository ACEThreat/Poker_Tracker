import customtkinter as ctk
from ...scraping.session_scraper import SessionScraper
from ...scraping.session_parser import SessionParser
from ...database.session_importer import SessionImporter
import threading
from tkinter import filedialog

class ImportTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.scraper = SessionScraper()
        self.parser = SessionParser()
        self.importer = SessionImporter()
        
        self._is_running = True
        
        # Create main content frame
        self.create_content_frame()
    
    def create_content_frame(self):
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Web Import Section
        web_frame = ctk.CTkFrame(content_frame)
        web_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        web_frame.grid_columnconfigure(0, weight=1)
        
        web_label = ctk.CTkLabel(web_frame, text="Import from Web:", font=("Arial", 12, "bold"))
        web_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Add instructions with increased wrap length
        instructions = (
            "Instructions: (Note: You must have Google Chrome installed)\n"
            "1. Ensure you are logged into your poker site in Chrome\n"
            "2. Close your Chrome browser (completely)\n"
            "3. Press Import Sessions\n"
            "4. The browser will open automatically and go to your poker site's session page\n"
            "5. Close any pop-ups the site loads\n"
            "6. Ensure that all the session data that you want to import is loaded on the page (it does not need to be visible)\n"
            "6. Return to the poker tracker and press \"Continue After Login\""
        )
        instructions_label = ctk.CTkLabel(web_frame, text=instructions, justify="left", wraplength=800)
        instructions_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Replace URL input with dropdown
        site_label = ctk.CTkLabel(web_frame, text="Select Site:")
        site_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.site_dropdown = ctk.CTkOptionMenu(
            web_frame,
            values=["Clubs Poker"],
            width=400
        )
        self.site_dropdown.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        # Import button
        self.import_button = ctk.CTkButton(
            web_frame,
            text="Import Sessions",
            command=self.start_import
        )
        self.import_button.grid(row=4, column=0, padx=5, pady=20)
        
        # File Import Section
        file_frame = ctk.CTkFrame(content_frame)
        file_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        file_frame.grid_columnconfigure(0, weight=1)
        
        file_label = ctk.CTkLabel(file_frame, text="Import from File:", font=("Arial", 12, "bold"))
        file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # File selection button
        self.file_button = ctk.CTkButton(
            file_frame,
            text="Select File",
            command=self.select_file
        )
        self.file_button.grid(row=1, column=0, padx=5, pady=20)
        
        # Status text
        self.status_text = ctk.CTkTextbox(content_frame, height=200)
        self.status_text.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Initially hidden buttons
        self.continue_button = ctk.CTkButton(
            content_frame,
            text="Continue After Login",
            command=self.continue_after_login
        )
        
        self.save_close_button = ctk.CTkButton(
            content_frame,
            text="Save & Close",
            command=self.save_and_close
        )
    
    def select_file(self):
        """Handle file selection and parsing"""
        file_path = filedialog.askopenfilename(
            title="Select Session File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.status_text.insert("1.0", f"Selected file: {file_path}\n")
            try:
                # Parse the file
                parsed_file = self.parser.parse_file(file_path)
                self.status_text.insert("1.0", f"File parsed successfully\n")
                
                # Get sessions data
                sessions = self.parser.get_sessions(parsed_file)
                
                # Import to database
                success, message = self.importer.import_sessions(sessions)
                if success:
                    self.status_text.insert("1.0", f"Database import successful: {len(sessions)} sessions imported\n")
                else:
                    self.status_text.insert("1.0", f"Database import failed: {message}\n")
                
            except Exception as e:
                self.status_text.insert("1.0", f"Error processing file: {str(e)}\n")
    
    def start_import(self):
        """Start the import process"""
        # Use hardcoded URL instead of entry
        url = "https://play.clubspoker.com/d/?my-games"
        
        self.status_text.insert("1.0", "Starting import process...\n")
        self.import_button.configure(state="disabled")
        
        def import_thread():
            try:
                if self.scraper.initialize_driver():
                    self.status_text.insert("1.0", "Browser initialized...\n")
                    if self.scraper.navigate_to_url(url):
                        self.status_text.insert("1.0", "Navigation successful...\n")
                        self.continue_button.grid(row=3, column=0, padx=5, pady=5)
            except Exception as e:
                self.status_text.insert("1.0", f"Error: {str(e)}\n")
                self.import_button.configure(state="normal")
        
        threading.Thread(target=import_thread).start()
    
    def continue_after_login(self):
        """Continue after manual login"""
        try:
            self.continue_button.grid_remove()
            
            if self.scraper.get_page_content():
                # Check if application is still running before updating GUI
                if hasattr(self, '_is_running') and not self._is_running:
                    return
                self.status_text.insert("1.0", "Content extracted successfully...\n")
                self.save_close_button.grid(row=4, column=0, padx=5, pady=5)
            else:
                if hasattr(self, '_is_running') and not self._is_running:
                    return
                self.status_text.insert("1.0", "Failed to extract content\n")
        except Exception as e:
            print(f"Error in continue_after_login: {str(e)}")
        finally:
            # Only try to update GUI if application is still running
            try:
                if hasattr(self, '_is_running') and self._is_running:
                    if hasattr(self, 'import_button'):
                        self.import_button.configure(state="normal")
            except Exception:
                pass
    
    def save_and_close(self):
        """Save content, parse sessions, import to database, and cleanup"""
        try:
            if not hasattr(self, '_is_running') or not self._is_running:
                return
            
            content_file = self.scraper.save_content()
            if content_file:
                self.status_text.insert("1.0", f"Content saved to: {content_file}\n")
                try:
                    parsed_file = self.parser.parse_file(content_file)
                    self.status_text.insert("1.0", f"Sessions parsed and saved to: {parsed_file}\n")
                    
                    sessions = self.parser.get_sessions(parsed_file)
                    success, message = self.importer.import_sessions(sessions)
                    
                    if success:
                        self.status_text.insert("1.0", f"Database import successful: {len(sessions)} sessions imported\n")
                        if self._is_running and hasattr(self.master, 'master') and hasattr(self.master.master, 'tabs'):
                            self.master.master.tabs["Sessions"].fetch_sessions()
                    else:
                        self.status_text.insert("1.0", f"Database import failed: {message}\n")
                    
                except Exception as e:
                    if self._is_running:
                        self.status_text.insert("1.0", f"Error during processing: {str(e)}\n")
        except Exception as e:
            print(f"Error in save_and_close: {str(e)}")
        finally:
            try:
                if self._is_running:
                    if hasattr(self, 'save_close_button'):
                        self.save_close_button.grid_remove()
                    if hasattr(self, 'import_button'):
                        self.import_button.configure(state="normal")
            except Exception:
                pass
    
    def cleanup(self):
        """Cleanup resources before destruction"""
        self._is_running = False
        if hasattr(self, 'scraper'):
            try:
                self.scraper.cleanup()
            except Exception:
                pass 