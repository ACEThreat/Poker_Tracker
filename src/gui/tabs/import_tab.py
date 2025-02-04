import customtkinter as ctk
from ...scraping.session_scraper import SessionScraper
from ...scraping.session_parser import SessionParser
from ...database.session_importer import SessionImporter
import threading
from tkinter import filedialog
from ...config import Config
import os
import json
import platform
import tkinter as tk

class ImportTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.scraper = SessionScraper()
        self.parser = SessionParser()
        self.importer = SessionImporter()
        
        self._is_running = True
        self.import_in_progress = False
        
        self.flash_count = 0
        self.flash_colors = ["#1f538d", "#2B93D1"]  # Dark blue to light blue
        
        # Create main content frame
        self.create_content_frame()
    
    def create_content_frame(self):
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # OS Detection Info Frame
        os_info_frame = ctk.CTkFrame(content_frame)
        os_info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        system = platform.system()
        os_label = ctk.CTkLabel(
            os_info_frame,
            text=f"🖥️ Detected OS: {system}",
            font=("Arial", 12, "bold")
        )
        os_label.pack(side="left", padx=10, pady=5)
        
        # Add current profile info
        self.profile_info_label = ctk.CTkLabel(
            os_info_frame,
            text=f"📂 Active Profile: Default",
            font=("Arial", 12, "bold")
        )
        self.profile_info_label.pack(side="right", padx=10, pady=5)
        
        # Web Import Section
        web_frame = ctk.CTkFrame(content_frame)
        web_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        web_frame.grid_columnconfigure(0, weight=1)
        
        # Add warning label
        warning_label = ctk.CTkLabel(
            web_frame, 
            text="⚠️ WARNING: You must be logged into the poker site in Google Chrome before proceeding! ⚠️",
            font=("Arial", 12, "bold"),
            text_color="red"
        )
        warning_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        web_label = ctk.CTkLabel(web_frame, text="Import from Web:", font=("Arial", 12, "bold"))
        web_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        instructions = (
            "Instructions: (Note: You must have Google Chrome installed)\n"
            "1. Ensure you are logged into your poker site in Chrome\n"
            "2. Close your Chrome browser (completely)\n"
            "3. Press Import Sessions\n"
            "4. The browser will open automatically and go to your poker site's session page\n"
            "5. Close any pop-ups the site loads\n"
            "6. Ensure that all the session data that you want to import is loaded on the page (it does not need to be visible)\n"
            "7. Press \"Continue after session history loaded\""
        )
        instructions_label = ctk.CTkLabel(web_frame, text=instructions, justify="left", wraplength=800)
        instructions_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        # Site selection dropdown
        site_label = ctk.CTkLabel(web_frame, text="Select Site:")
        site_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        self.site_dropdown = ctk.CTkOptionMenu(
            web_frame,
            values=["Clubs Poker"],
            width=400
        )
        self.site_dropdown.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        # Button frame for import controls
        import_button_frame = ctk.CTkFrame(web_frame)
        import_button_frame.grid(row=5, column=0, padx=5, pady=20)
        
        # Import button
        self.import_button = ctk.CTkButton(
            import_button_frame,
            text="Import Sessions",
            command=self.start_import,
            width=150
        )
        self.import_button.pack(side="left", padx=5)
        
        # Stop button (initially disabled)
        self.stop_button = ctk.CTkButton(
            import_button_frame,
            text="Stop Import",
            command=self.stop_import,
            width=150,
            state="disabled",
            fg_color="#D22B2B",  # Red color for stop button
            hover_color="#AA0000"
        )
        self.stop_button.pack(side="left", padx=5)
        
        # File Import Section
        file_frame = ctk.CTkFrame(content_frame)
        file_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        
        file_label = ctk.CTkLabel(file_frame, text="Import from File:", font=("Arial", 12, "bold"))
        file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # File selection button
        self.file_button = ctk.CTkButton(
            file_frame,
            text="Select File",
            command=self.select_file
        )
        self.file_button.grid(row=1, column=0, padx=5, pady=20)
        
        # Initially hidden buttons - place them before the status text
        self.continue_button = ctk.CTkButton(
            web_frame,  # Changed from content_frame to web_frame
            text="Continue after session history loaded",
            command=self.continue_after_login,
            width=300,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="#1f538d"  # Added distinctive color
        )
        self.continue_button.grid(row=5, column=0, padx=5, pady=10, sticky="ew")
        self.continue_button.grid_remove()  # Hide initially
        
        # Status text - moved after the continue button
        self.status_text = ctk.CTkTextbox(content_frame, height=200)
        self.status_text.grid(row=7, column=0, padx=5, pady=5, sticky="ew")
        
        # Save & Close button
        self.save_close_button = ctk.CTkButton(
            web_frame,  # Changed from content_frame to web_frame
            text="Save & Close",
            command=self.save_and_close,
            width=300,
            font=("Arial", 14, "bold")
        )
        self.save_close_button.grid(row=8, column=0, padx=5, pady=5, sticky="ew")
        self.save_close_button.grid_remove()  # Hide initially

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
    
    def start_flash_effect(self):
        """Start the flashing effect for the continue button"""
        self.flash_count = 0
        self.flash_button()

    def flash_button(self):
        """Create a flashing effect for the continue button"""
        if self.flash_count < 6 and hasattr(self, '_is_running') and self._is_running:  # Flash 3 times (6 color changes)
            current_color = self.flash_colors[self.flash_count % 2]
            self.continue_button.configure(fg_color=current_color)
            self.flash_count += 1
            self.after(500, self.flash_button)  # Flash every 500ms
        else:
            # Reset to default color
            self.continue_button.configure(fg_color=self.flash_colors[0])

    def start_import(self):
        """Start the import process"""
        url = "https://play.clubspoker.com/d/?my-games"
        
        self.status_text.insert("1.0", "Starting import process...\n")
        self.import_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        def status_callback(message):
            self.status_text.insert("1.0", message)
        
        def import_thread():
            try:
                self.scraper.set_status_callback(status_callback)
                if self.scraper.initialize_driver():
                    self.status_text.insert("1.0", "Browser initialized...\n")
                    if self.scraper.navigate_to_url(url):
                        self.status_text.insert("1.0", "Navigation successful...\n")
                        self.continue_button.grid()
                        self.continue_button.lift()
                    else:
                        self.status_text.insert("1.0", "Failed to navigate to URL\n")
                        self.reset_import_state()
                else:
                    self.status_text.insert("1.0", "Failed to initialize browser\n")
                    self.reset_import_state()
            except Exception as e:
                self.status_text.insert("1.0", f"Error: {str(e)}\n")
                self.reset_import_state()
        
        threading.Thread(target=import_thread).start()

    def stop_import(self):
        """Stop the import process and reset the UI"""
        self.import_in_progress = False
        self.flash_count = 6  # Stop any ongoing flash effect
        
        # Close any open verification windows
        try:
            for widget in self.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
        except Exception:
            pass
        
        # Cleanup scraper
        if hasattr(self, 'scraper'):
            self.scraper.cleanup()
            self.scraper = SessionScraper()
        
        self.reset_import_state()
        self.status_text.insert("1.0", "Import process stopped by user\n")

    def reset_import_state(self):
        """Reset the UI to its default state"""
        self.import_in_progress = False
        self.import_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        # Remove continue and save/close buttons if they exist
        if hasattr(self, 'continue_button'):
            self.continue_button.grid_remove()
        if hasattr(self, 'save_close_button'):
            self.save_close_button.grid_remove()

    def continue_after_login(self):
        """Continue after manual login"""
        try:
            self.continue_button.grid_remove()
            
            if self.scraper.get_page_content():
                # Check if application is still running before updating GUI
                if hasattr(self, '_is_running') and not self._is_running:
                    return
                self.status_text.insert("1.0", "Content extracted successfully...\n")
                self.save_close_button.grid(row=8, column=0, padx=5, pady=5, sticky="ew")
            else:
                if hasattr(self, '_is_running') and not self._is_running:
                    return
                self.status_text.insert("1.0", "Failed to extract content\n")
                self.import_button.configure(state="normal")
        except Exception as e:
            self.status_text.insert("1.0", f"Error in continue_after_login: {str(e)}\n")
            self.import_button.configure(state="normal")
    
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
        self.import_in_progress = False
        if hasattr(self, 'scraper'):
            try:
                self.scraper.cleanup()
            except Exception:
                pass

    def update_chrome_path(self, profile_name):
        """Update Chrome path when profile is selected"""
        system = platform.system()
        if system in Config.CHROME_PROFILES:
            if system == 'Windows':
                username = os.getenv('USERNAME')
                base_path = Config.CHROME_PROFILES[system][profile_name].format(username=username)
            else:
                base_path = os.path.expanduser(Config.CHROME_PROFILES[system][profile_name])
            
            self.chrome_path_var.set(base_path)
            self.profile_info_label.configure(text=f"📂 Active Profile: {profile_name}")
            self.status_text.insert("1.0", f"Updated Chrome profile path for {profile_name}\n")
        else:
            self.status_text.insert("1.0", f"Warning: Unsupported OS detected: {system}\n")

    def on_os_change(self, selected_os):
        """Handle OS selection change"""
        try:
            # Update profiles dropdown
            profiles = list(Config.CHROME_PROFILES.get(selected_os, {}).keys())
            self.profile_var.set("Default")
            
            # Update chrome path based on new OS
            if selected_os == 'Windows':
                username = os.getenv('USERNAME')
                default_path = Config.CHROME_PROFILES[selected_os]["Default"].format(username=username)
            else:
                default_path = os.path.expanduser(Config.CHROME_PROFILES[selected_os]["Default"])
            
            self.chrome_path_var.set(default_path)
            self.status_text.insert("1.0", f"Updated to {selected_os} default Chrome path\n")
        except Exception as e:
            self.status_text.insert("1.0", f"Error updating OS settings: {str(e)}\n") 