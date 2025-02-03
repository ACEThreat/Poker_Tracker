import customtkinter as ctk
from pathlib import Path
import os

# Update these imports to use absolute paths
from poker_tracker.src.gui.tabs.bankroll_overview_tab import BankrollOverviewTab
from poker_tracker.src.gui.tabs.sessions_tab import SessionsTab
from poker_tracker.src.gui.tabs.stats_tab import StatsTab
from poker_tracker.src.gui.tabs.settings_tab import SettingsTab
from poker_tracker.src.gui.tabs.import_tab import ImportTab
from ..database.database import Database
from ..config import Config

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Ensure all required directories exist
        Config.ensure_directories()
        
        # Set window size for 1080p (1920x1080)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.title("Poker Tracker")
        
        # Configure main window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Row 0 is for tabs, Row 1 for content
        
        # Create tabs at the top
        self.create_tab_buttons()
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize tabs
        self.current_tab = None
        self.tabs = {}
        self.setup_tabs()
        
        # Show default tab
        self.show_tab("Bankroll Overview")
        
        # Bind the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_tab_buttons(self):
        tab_frame = ctk.CTkFrame(self)
        tab_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        tabs = ["Bankroll Overview", "Sessions", "Stats", "Settings", "Import"]
        for i, tab_name in enumerate(tabs):
            btn = ctk.CTkButton(
                tab_frame,
                text=tab_name,
                command=lambda t=tab_name: self.show_tab(t),
                width=120
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
            
    def setup_tabs(self):
        # Create tab instances
        self.tabs["Bankroll Overview"] = BankrollOverviewTab(self.content_frame)
        self.tabs["Sessions"] = SessionsTab(self.content_frame)
        self.tabs["Stats"] = StatsTab(self.content_frame)
        self.tabs["Settings"] = SettingsTab(self.content_frame)
        self.tabs["Import"] = ImportTab(self.content_frame)
        
        # Initially hide all tabs
        for tab in self.tabs.values():
            tab.grid_remove()
    
    def show_tab(self, tab_name):
        # Hide current tab if exists
        if self.current_tab:
            self.tabs[self.current_tab].grid_remove()
        
        # Show selected tab
        self.tabs[tab_name].grid(row=0, column=0, sticky="nsew")
        self.current_tab = tab_name

    def on_closing(self):
        """Handle window closing"""
        try:
            if hasattr(self, 'tabs'):
                for tab in self.tabs.values():
                    if hasattr(tab, 'cleanup'):
                        tab.cleanup()
        finally:
            self.quit()

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
