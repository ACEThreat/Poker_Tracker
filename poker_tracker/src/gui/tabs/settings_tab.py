import customtkinter as ctk
from tkinter import messagebox
from ...database.database import Database
from sqlalchemy import text

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