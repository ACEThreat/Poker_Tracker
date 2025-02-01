import customtkinter as ctk
from tkinter import messagebox
from ...database.database import Database
from sqlalchemy import text
import shutil
from datetime import datetime
from ...config import Config
import os

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Add placeholder label
        ctk.CTkLabel(self, text="Settings Tab Content").grid(
            row=0, column=0, padx=20, pady=20
        )
        
        # Create Database Actions section
        self.create_database_section()
        
        # Create Backup section
        self.create_backup_section()
        
    def create_database_section(self):
        # Database section frame
        db_frame = ctk.CTkFrame(self)
        db_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Section header
        header = ctk.CTkLabel(
            db_frame, 
            text="Database Actions",
            font=("Arial", 14, "bold")
        )
        header.pack(pady=10)
        
        # Refresh Database button
        refresh_btn = ctk.CTkButton(
            db_frame,
            text="Refresh Database",
            command=self.refresh_database,
            width=200
        )
        refresh_btn.pack(pady=5)
        
        # Delete All Sessions button
        delete_btn = ctk.CTkButton(
            db_frame,
            text="Delete All Sessions",
            command=self.confirm_delete_sessions,
            width=200,
            fg_color="darkred",
            hover_color="red"
        )
        delete_btn.pack(pady=5)
        
    def create_backup_section(self):
        backup_frame = ctk.CTkFrame(self)
        backup_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Section header
        header = ctk.CTkLabel(
            backup_frame, 
            text="Database Backup",
            font=("Arial", 14, "bold")
        )
        header.pack(pady=10)
        
        # Create Backup button
        backup_btn = ctk.CTkButton(
            backup_frame,
            text="Create Backup",
            command=self.create_backup,
            width=200
        )
        backup_btn.pack(pady=5)
        
        # Restore Backup button
        restore_btn = ctk.CTkButton(
            backup_frame,
            text="Restore Backup",
            command=self.restore_backup,
            width=200,
            fg_color="#2B5EA7",
            hover_color="#1E4175"
        )
        restore_btn.pack(pady=5)
        
    def refresh_database(self):
        try:
            db = Database()
            session = db.get_session()
            session.close()
            messagebox.showinfo("Success", "Database refreshed successfully")
            # Update sessions tab through the main window's tabs dictionary
            self.master.tabs["Sessions"].fetch_sessions()
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