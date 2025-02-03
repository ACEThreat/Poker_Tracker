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
        
        # Load or create default Chrome profile path
        self.chrome_profile = self.load_chrome_profile()
        
        self.flash_count = 0
        self.flash_colors = ["#1f538d", "#2B93D1"]  # Dark blue to light blue
        
        # Create main content frame
        self.create_content_frame()
    
    def load_chrome_profile(self):
        """Load Chrome profile path from config or set default"""
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    if 'chrome_profile' in config:
                        return config['chrome_profile']
            except Exception as e:
                print(f"Error reading config file: {e}")
        
        # Get default path based on OS
        system = platform.system()
        if system == 'Windows':
            username = os.getenv('USERNAME')
            default_path = rf'C:\Users\{username}\AppData\Local\Google\Chrome\User Data'
        elif system == 'Darwin':  # macOS
            default_path = os.path.expanduser('~/Library/Application Support/Google/Chrome/User Data')
        elif system == 'Linux':
            default_path = os.path.expanduser('~/.config/google-chrome')
        else:
            default_path = ''
        
        return default_path

    def save_chrome_profile(self, path):
        """Save Chrome profile path to config"""
        Config.ensure_directories()
        try:
            config = {}
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            config['chrome_profile'] = path
            
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def create_content_frame(self):
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # OS Detection Info Frame
        os_info_frame = ctk.CTkFrame(content_frame)
        os_info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
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
        
        # Chrome Profile Section
        chrome_frame = ctk.CTkFrame(content_frame)
        chrome_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        chrome_frame.grid_columnconfigure(1, weight=1)
        
        chrome_label = ctk.CTkLabel(
            chrome_frame, 
            text="Chrome Profile Path:", 
            font=("Arial", 12, "bold")
        )
        chrome_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.chrome_path_var = ctk.StringVar(value=self.chrome_profile)
        self.chrome_path_entry = ctk.CTkEntry(
            chrome_frame,
            textvariable=self.chrome_path_var,
            width=400
        )
        self.chrome_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Profile selection frame
        profile_frame = ctk.CTkFrame(chrome_frame)
        profile_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        profile_label = ctk.CTkLabel(
            profile_frame,
            text="Chrome Profile:",
            font=("Arial", 12, "bold")
        )
        profile_label.pack(side="left", padx=5)
        
        system = platform.system()
        profiles = list(Config.CHROME_PROFILES.get(system, {}).keys())
        
        self.profile_var = ctk.StringVar(value="Default")
        profile_dropdown = ctk.CTkOptionMenu(
            profile_frame,
            values=profiles,
            variable=self.profile_var,
            command=self.update_chrome_path
        )
        profile_dropdown.pack(side="left", padx=5)
        
        save_path_button = ctk.CTkButton(
            chrome_frame,
            text="Save Path",
            command=self.save_path,
            width=100
        )
        save_path_button.grid(row=0, column=2, padx=5, pady=5)
        
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
        file_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
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
        self.status_text.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # Initially hidden buttons
        self.continue_button = ctk.CTkButton(
            content_frame,
            text="Continue after session history loaded",  # Updated button text
            command=self.continue_after_login,
            width=300,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=self.flash_colors[0],
            hover_color="#1D4B7E"
        )
        
        self.save_close_button = ctk.CTkButton(
            content_frame,
            text="Save & Close",
            command=self.save_and_close
        )

    def save_path(self):
        """Save the Chrome profile path"""
        path = self.chrome_path_var.get()
        if os.path.exists(os.path.dirname(path)):
            self.save_chrome_profile(path)
            self.chrome_profile = path
            self.status_text.insert("1.0", "Chrome profile path saved successfully\n")
        else:
            self.status_text.insert("1.0", "Error: Invalid path. Please enter a valid Chrome profile path\n")

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
        self.import_in_progress = True
        
        def import_thread():
            try:
                if not self.import_in_progress:
                    return
                
                if self.scraper.initialize_driver(chrome_profile=self.chrome_path_var.get()):
                    self.status_text.insert("1.0", "Browser initialized...\n")
                    if self.import_in_progress and self.scraper.navigate_to_url(url):
                        self.status_text.insert("1.0", "Navigation successful...\n")
                        self.continue_button.grid(row=4, column=0, padx=5, pady=5)
                        # Start the flashing effect
                        self.after(0, self.start_flash_effect)
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