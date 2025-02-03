import os
from pathlib import Path
import json
import platform
from tkinter import messagebox, Tk, simpledialog
import time

class Config:
    APP_DIR = os.path.expanduser('~/.poker_tracker')
    DB_NAME = 'database.db'
    LOG_DIR = os.path.join(APP_DIR, 'logs')
    IMPORT_DIR = os.path.join(APP_DIR, 'DB_Import_Files')
    BACKUP_DIR = os.path.join(APP_DIR, 'backups')
    CONFIG_FILE = os.path.join(APP_DIR, 'config.json')
    
    # Default Chrome profile paths by OS
    DEFAULT_CHROME_PATHS = {
        'Windows': r'C:\Users\{username}\AppData\Local\Google\Chrome\User Data',
        'Darwin': '~/Library/Application Support/Google/Chrome/User Data',  # Updated macOS path
        'Linux': '~/.config/google-chrome'
    }
    
    # Add to existing DEFAULT_CHROME_PATHS
    CHROME_PROFILES = {
        'Windows': {
            'Default': r'C:\Users\{username}\AppData\Local\Google\Chrome\User Data',
            'Profile 1': r'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Profile 1',
            'Profile 2': r'C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Profile 2'
        },
        'Darwin': {  # macOS
            'Default': '~/Library/Application Support/Google/Chrome/User Data',
            'Profile 1': '~/Library/Application Support/Google/Chrome/User Data/Profile 1',
            'Profile 2': '~/Library/Application Support/Google/Chrome/User Data/Profile 2'
        },
        'Linux': {
            'Default': '~/.config/google-chrome',
            'Profile 1': '~/.config/google-chrome/Profile 1',
            'Profile 2': '~/.config/google-chrome/Profile 2'
        }
    }
    
    @classmethod
    def get_chrome_profile(cls):
        """Get Chrome profile path, prompting user on first run"""
        # Check if we have a stored config
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    if 'chrome_profile' in config:
                        return config['chrome_profile']
            except Exception as e:
                print(f"Error reading config file: {e}")
        
        # Get default path for current OS
        system = platform.system()
        default_path = os.path.expanduser(cls.DEFAULT_CHROME_PATHS.get(system, ''))
        
        # Prepare OS-specific instructions
        instructions = {
            'Darwin': """
Please enter your Chrome profile path.
Default location on macOS:
~/Library/Application Support/Google/Chrome

To find your profile:
1. Open Chrome
2. Go to chrome://version
3. Look for 'Profile Path'
""",
            'Windows': """
Please enter your Chrome profile path.
Default location on Windows:
%LOCALAPPDATA%\\Google\\Chrome\\User Data

To find your profile:
1. Open Chrome
2. Go to chrome://version
3. Look for 'Profile Path'
""",
            'Linux': """
Please enter your Chrome profile path.
Default location on Linux:
~/.config/google-chrome

To find your profile:
1. Open Chrome
2. Go to chrome://version
3. Look for 'Profile Path'
"""
        }

        chrome_path = None
        root = None
        
        try:
            root = Tk()
            root.withdraw()  # Hide the main window
            
            # Make sure the window is ready
            root.update()
            
            # Show instructions and get path from user
            chrome_path = simpledialog.askstring(
                "Chrome Profile Path",
                instructions.get(system, "Please enter your Chrome profile path:"),
                initialvalue=default_path,
                parent=root
            )
            
            # Give the dialog time to complete
            time.sleep(0.1)
            root.update()
            
        except Exception as e:
            print(f"Error showing dialog: {e}")
        finally:
            if root:
                try:
                    root.destroy()
                except Exception:
                    pass

        if not chrome_path:
            messagebox.showerror(
                "Error",
                "Chrome profile path is required for session importing. "
                "Please restart the application and provide a valid path."
            )
            raise SystemExit(1)
        
        # Expand user path if necessary
        chrome_path = os.path.expanduser(chrome_path)
        
        # Verify path exists
        if not os.path.exists(chrome_path):
            messagebox.showerror(
                "Error",
                f"The specified path does not exist:\n{chrome_path}\n\n"
                "Please restart the application and provide a valid path."
            )
            raise SystemExit(1)
        
        # Save the config
        cls.ensure_directories()
        try:
            config = {}
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            config['chrome_profile'] = chrome_path
            
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config file: {e}")
        
        return chrome_path
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.APP_DIR, cls.LOG_DIR, cls.IMPORT_DIR, cls.BACKUP_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True) 