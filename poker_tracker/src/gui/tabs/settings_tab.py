import customtkinter as ctk
from tkinter import messagebox
from ...database.database import Database
from sqlalchemy import text
import shutil
from datetime import datetime
from ...config import Config
import os
import webbrowser
import platform

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=0)  # Adjust row weights
        
        # Create main container frame
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create sections
        self.create_tools_section()
        self.create_database_section()
        self.create_backup_section()
        
    def create_tools_section(self):
        """Create Tools section with quick access features"""
        tools_frame = ctk.CTkFrame(self.main_container)
        tools_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Section header with icon-like character
        header_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 5))
        
        header = ctk.CTkLabel(
            header_frame, 
            text="🛠️ Quick Tools",
            font=("Arial", 16, "bold")
        )
        header.pack(side="left", padx=10)
        
        # Separator
        separator = ctk.CTkFrame(tools_frame, height=2, fg_color="gray50")
        separator.pack(fill="x", padx=10, pady=(0, 10))
        
        # Open Poker Site button
        open_site_btn = ctk.CTkButton(
            tools_frame,
            text="🌐 Open Poker Site",
            command=self.open_poker_site,
            width=200,
            height=40,
            fg_color="#2B5EA7",
            hover_color="#1E4175",
            font=("Arial", 13)
        )
        open_site_btn.pack(pady=10, padx=20)
        
    def create_database_section(self):
        """Create Database Actions section"""
        db_frame = ctk.CTkFrame(self.main_container)
        db_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Section header with icon
        header_frame = ctk.CTkFrame(db_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 5))
        
        header = ctk.CTkLabel(
            header_frame, 
            text="🗄️ Database Actions",
            font=("Arial", 16, "bold")
        )
        header.pack(side="left", padx=10)
        
        # Separator
        separator = ctk.CTkFrame(db_frame, height=2, fg_color="gray50")
        separator.pack(fill="x", padx=10, pady=(0, 10))
        
        # Button container for better spacing
        button_container = ctk.CTkFrame(db_frame, fg_color="transparent")
        button_container.pack(pady=10, padx=20)
        
        # Refresh Database button
        refresh_btn = ctk.CTkButton(
            button_container,
            text="🔄 Refresh Database",
            command=self.refresh_database,
            width=200,
            height=40,
            font=("Arial", 13)
        )
        refresh_btn.pack(pady=5)
        
        # Delete All Sessions button
        delete_btn = ctk.CTkButton(
            button_container,
            text="🗑️ Delete All Sessions",
            command=self.confirm_delete_sessions,
            width=200,
            height=40,
            fg_color="darkred",
            hover_color="#8B0000",
            font=("Arial", 13)
        )
        delete_btn.pack(pady=5)
        
    def create_backup_section(self):
        """Create Backup section"""
        backup_frame = ctk.CTkFrame(self.main_container)
        backup_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Section header with icon
        header_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 5))
        
        header = ctk.CTkLabel(
            header_frame, 
            text="💾 Backup & Restore",
            font=("Arial", 16, "bold")
        )
        header.pack(side="left", padx=10)
        
        # Separator
        separator = ctk.CTkFrame(backup_frame, height=2, fg_color="gray50")
        separator.pack(fill="x", padx=10, pady=(0, 10))
        
        # Button container
        button_container = ctk.CTkFrame(backup_frame, fg_color="transparent")
        button_container.pack(pady=10, padx=20)
        
        # Create Backup button
        backup_btn = ctk.CTkButton(
            button_container,
            text="📥 Create Backup",
            command=self.create_backup,
            width=200,
            height=40,
            font=("Arial", 13)
        )
        backup_btn.pack(pady=5)
        
        # Restore Backup button
        restore_btn = ctk.CTkButton(
            button_container,
            text="📤 Restore Backup",
            command=self.restore_backup,
            width=200,
            height=40,
            fg_color="#2B5EA7",
            hover_color="#1E4175",
            font=("Arial", 13)
        )
        restore_btn.pack(pady=5)
        
    def refresh_database(self):
        try:
            db = Database()
            db.update_total_hours()  # Update any calculations if needed
            
            # Get main window and refresh sessions if possible
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'tabs') and "Sessions" in main_window.tabs:
                main_window.tabs["Sessions"].fetch_sessions()
            
            messagebox.showinfo("Success", "Database refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh database: {str(e)}")
            
    def confirm_delete_sessions(self):
        if messagebox.askyesno("Confirm Delete", 
            "Are you sure you want to delete ALL sessions?\nThis action cannot be undone."):
            self.delete_all_sessions()
            
    def delete_all_sessions(self):
        try:
            db = Database()
            session = db.get_session()
            session.execute(text("DELETE FROM sessions"))
            session.commit()
            session.close()
            messagebox.showinfo("Success", "All sessions deleted successfully")
            # Update sessions tab through the main window's tabs dictionary
            self.master.tabs["Sessions"].fetch_sessions()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete sessions: {str(e)}")
            
    def create_backup(self):
        try:
            db_path = os.path.join(Config.APP_DIR, Config.DB_NAME)
            if not os.path.exists(db_path):
                messagebox.showerror("Error", "Database file not found")
                return
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(Config.BACKUP_DIR, f'database_backup_{timestamp}.db')
            
            # Close current database connection
            db = Database()
            session = db.get_session()
            session.close()
            db.engine.dispose()
            
            # Copy database file
            shutil.copy2(db_path, backup_path)
            messagebox.showinfo("Success", f"Backup created successfully\nLocation: {backup_path}")
            
            # Open backup folder
            os.system(f'open "{Config.BACKUP_DIR}"')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")
            
    def restore_backup(self):
        try:
            backups = sorted([f for f in os.listdir(Config.BACKUP_DIR) 
                            if f.startswith('database_backup_')], reverse=True)
            
            if not backups:
                messagebox.showinfo("Info", "No backups found")
                return
                
            # Create backup selection window
            select_window = ctk.CTkToplevel(self)
            select_window.title("Select Backup")
            select_window.geometry("400x300")
            
            # Create scrollable frame for backups
            scroll_frame = ctk.CTkScrollableFrame(select_window)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            def restore_selected(backup_file):
                if messagebox.askyesno("Confirm Restore", 
                    "Are you sure you want to restore this backup?\nCurrent data will be replaced."):
                    try:
                        db_path = os.path.join(Config.APP_DIR, Config.DB_NAME)
                        backup_path = os.path.join(Config.BACKUP_DIR, backup_file)
                        
                        # Close current database connection
                        db = Database()
                        session = db.get_session()
                        session.close()
                        db.engine.dispose()
                        
                        # Create backup of current database before restoring
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        pre_restore_backup = os.path.join(Config.BACKUP_DIR, 
                                                        f'pre_restore_backup_{timestamp}.db')
                        shutil.copy2(db_path, pre_restore_backup)
                        
                        # Restore selected backup
                        shutil.copy2(backup_path, db_path)
                        
                        messagebox.showinfo("Success", "Database restored successfully")
                        select_window.destroy()
                        
                        # Update sessions tab through the main window
                        main_window = self.winfo_toplevel()
                        if hasattr(main_window, 'tabs') and "Sessions" in main_window.tabs:
                            main_window.tabs["Sessions"].fetch_sessions()
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")
            
            # Add backup files as buttons
            for backup in backups:
                timestamp = backup.replace('database_backup_', '').replace('.db', '')
                formatted_date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                
                btn = ctk.CTkButton(
                    scroll_frame,
                    text=f"Backup from {formatted_date}",
                    command=lambda b=backup: restore_selected(b)
                )
                btn.pack(pady=5, padx=10, fill="x")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list backups: {str(e)}")

    def open_poker_site(self):
        """Open the poker site in default Chrome browser across different operating systems"""
        url = "https://play.clubspoker.com/d/?my-games"
        try:
            # Try to open specifically in Chrome based on OS
            system = platform.system()
            if system == 'Darwin':  # macOS
                chrome_path = r'open -a "/Applications/Google Chrome.app" %s'
            elif system == 'Windows':
                chrome_path = r'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
            elif system == 'Linux':
                chrome_path = r'/usr/bin/google-chrome %s'
            else:
                chrome_path = None
            
            if chrome_path:
                browser = webbrowser.get(chrome_path)
                browser.open(url)
            else:
                # Fallback to default browser if Chrome path not found
                webbrowser.open(url)
                
            messagebox.showinfo("Success", "Opening poker site in browser")
        except Exception as e:
            # Fallback to default browser if Chrome fails
            try:
                webbrowser.open(url)
                messagebox.showinfo("Success", "Opening poker site in default browser")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open poker site: {str(e)}") 